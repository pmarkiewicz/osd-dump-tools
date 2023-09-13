from __future__ import annotations

import pathlib
import struct
import sys
import time
from configparser import ConfigParser
from subprocess import Popen
import re

import pysrt
import ffmpeg

from .render import DjiRenderer, WsRenderer
from .frame import Frame, SrtFrame
from .font import Font
from .const import CONFIG_FILE_NAME, OSD_TYPE_DJI, OSD_TYPE_WS, FW_ARDU, FW_INAV, FW_BETAFL, FW_UNKNOWN
from .config import Config
from .utils.codecs import find_codec
from .utils.find_slot import find_slots
from .utils.fps import get_fps
from .utils.time_to_ms import time_to_milliseconds
from .cmd_line import build_cmd_line_parser
from .dji import read_dji_osd_frames
from .ws import read_ws_osd_frames


file_header_struct_detect = struct.Struct("<4s")
# < little-endian
# 4s string


def detect_system(osd_path: pathlib.Path, verbatim: bool = False) -> tuple :
    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_detect.size)
        file_header = file_header_struct_detect.unpack(file_header_data)

        if file_header[0] == b'MSPO':
            return OSD_TYPE_DJI, FW_UNKNOWN
        if file_header[0] == b'INAV':
            return OSD_TYPE_WS, FW_INAV
        if file_header[0] == b'BTFL':
            return OSD_TYPE_WS, FW_BETAFL
        if file_header[0] == b'ARDU':
            return OSD_TYPE_WS, FW_ARDU

        print(f"{osd_path} has an invalid file header")
        sys.exit(1)




def get_renderer(osd_type: int):
    if osd_type == OSD_TYPE_DJI:
        return DjiRenderer

    return WsRenderer


def render_test_frame(frames: list[Frame], srt_frames: list[SrtFrame], font: Font, cfg: Config, osd_type: int, video_path: pathlib.Path) -> None:
    test_frame = osd_frame_idx(frames, args.testframe)
    srt_idxs = [srt.idx for srt in srt_frames]
    srt_slot = find_slots(srt_idxs, args.testframe, args.testframe+1)
    srt_idx = None
    if srt_slot:
        srt_idx = srt_slot[0]
    test_path = str(video_path.with_name('test_image.png'))
    print(f"test frame created: {test_path}")
    cls = get_renderer(osd_type)
    renderer = cls(font=font, cfg=cfg, osd_type=osd_type, frames=frames, srt_frames=srt_frames)
    renderer.render_test_frame(
            test_frame,
            srt_idx
        ).save(test_path)

    return


def render_frames(frames: list[Frame], srt_frames: list[SrtFrame], font: Font, cfg: Config, osd_type: int, video_path: pathlib.Path, out_path: pathlib.Path) -> None:
    print(f"rendering {len(frames)} frames")

    cls = get_renderer(osd_type)
    renderer = cls(font, cfg, osd_type, frames, srt_frames)

    for i in range(len(frames)-1):
        if frames[i].next_idx != frames[i+1].idx:
            print(f'incorrect frame {frames[i].next_idx}')

    frames_idx_render = []
    if srt_frames:
        srt_idxs = [srt.idx for srt in srt_frames]

        for idx, frame in enumerate(frames[:-1]):
            start_frame = frame.idx
            next_frame = frame.next_idx
            frames = find_slots(srt_idxs, start_frame, next_frame)
            frames_idx_render.append((idx, frames,))
    else:
        frames_idx_render = [(idx, None,) for frame in frames[:-1]]
        
    process = run_ffmpeg_stdin(cfg, video_path, out_path)
    total_time = 0
    for img in renderer.render_single_frame_in_memory(frames_idx_render):
        ts = time.time_ns()
        process.stdin.write(img)
        total_time += (time.time_ns() - ts)

    # Close the pipe to signal the end of input
    process.stdin.close()

    # Wait for ffmpeg to finish
    process.wait()


def run_ffmpeg_stdin(cfg: Config, video_path: pathlib.Path, out_path: pathlib.Path) -> Popen[bytes]:
    codec = find_codec()
    if not codec:
        print('No ffmpeg codec found')
        sys.exit(2)

    if cfg.verbatim:
        print(f'Found a working codec: {codec}')

    frame_overlay = ffmpeg.input('pipe:', framerate=60, thread_queue_size=65536, vcodec="png")  # format="image2pipe", 
    video = ffmpeg.input(str(video_path), thread_queue_size=4096, hwaccel="auto")

    out_size = {"w": cfg.target_width, "h": cfg.target_height}

    output_params = {
        'video_bitrate': f"{cfg.bitrate}M",
        'c:v': codec,
        'acodec': 'copy',
    }

    # from https://ffmpeg.org/faq.html#Which-are-good-parameters-for-encoding-high-quality-MPEG_002d4_003f
    hq_output = {
        'mbd': 'rd',
        'flags': '+mv4+aic',
        'trellis': 2,
        'cmp': 2,
        'subcmp': 2,
        'g': 300,
        'bf': 2,
    }

    if args.hq:
        output_params.update(hq_output)

    return video.filter("scale", **out_size, force_original_aspect_ratio=1) \
        .filter("pad", **out_size, x=-1, y=-1, color="black") \
        .overlay(frame_overlay, x=0, y=0) \
        .output(str(out_path), **output_params) \
        .global_args('-loglevel', 'info' if args.ffmpeg_verbatim else 'error') \
        .global_args('-stats') \
        .global_args('-hide_banner') \
        .overwrite_output() \
        .run_async(pipe_stdin=True)


def read_srt_frames(srt_path: pathlib.Path, verbatim: bool, fps: int) -> list[SrtFrame]:
    frames_per_ms = (1 / fps) * 1000

    if verbatim:
        print(f'Loading srt data from {srt_path}')
    subs = pysrt.open(srt_path)

    result = []
    pattern = r'[-+]?\d*\.\d+|\d+'

    for sub in subs:
        items = sub.text.split(' ')
        d = {}
        for item in items:
            name, val = item.lower().split(':')
            val = re.search(pattern, val).group()
            try:
                val = int(val)
            except ValueError:
                val = float(val)
            d[name] = val

        ms = time_to_milliseconds(sub.start.to_time())
        frame_idx = int(ms // frames_per_ms)
        d['start_time'] = ms
        d['idx'] = frame_idx
        frame = SrtFrame(**d)
        result.append(frame)

    return result


def osd_frame_idx(frames: list[Frame], frame_no: int) -> int | None:
    """
    Finds frame in list of osd frames that is inside range
    """
    left, right = 0, len(frames) - 1

    while left <= right:
        middle = (left + right) // 2
        frame = frames[middle]

        if frame.idx <= frame_no < frame.next_idx:
            return middle

        if frame_no < frame.idx:
            right = middle - 1

        elif frame_no >= frame.next_idx:
            left = middle + 1

    return None


def main(args: Config):
    print(f"loading fonts from: {args.font}")

    if args.hd:
        font = Font(f"{args.font}_hd", is_hd=True, small_font_scale=args.srt_font_scale)
    else:
        font = Font(args.font, is_hd=False, small_font_scale=args.srt_font_scale)

    video_path = pathlib.Path(args.video)
    video_stem = video_path.stem
    osd_path = video_path.with_suffix('.osd')
    srt_path = video_path.with_suffix('.srt')
    out_path = video_path.with_name(video_stem + "_with_osd.mp4")

    # TODO: extract to validate function?
    if not video_path.exists():
        print(f'Video file "{video_path}" does not exists. Terminating.')
        sys.exit(2)

    if not osd_path.exists():
        print(f'OSD file "{osd_path}" does not exists. Terminating.')
        sys.exit(2)

    srt_exists = srt_path.exists()

    fps = get_fps(video_path)

    print(f"verbatim:  {args.verbatim}")
    print(f"loading OSD dump from:  {osd_path}")

    osd_type, firmware = detect_system(osd_path)

    srt_frames = []
    if srt_exists:
        srt_frames = read_srt_frames(srt_path, args.verbatim, fps)

    if osd_type == OSD_TYPE_DJI:
        frames = read_dji_osd_frames(osd_path, args.verbatim, args)
    else:
        frames = read_ws_osd_frames(osd_path, args.verbatim, args)

    if args.testrun:
        render_test_frame(frames, srt_frames, font, args, osd_type, video_path)
        return

    render_frames(frames, srt_frames, font, args, osd_type, video_path, out_path)


if __name__ == "__main__":
    cfg = ConfigParser()
    cfg.read(pathlib.PurePath(__file__).parent / CONFIG_FILE_NAME)
    cfg.read(CONFIG_FILE_NAME)

    parser = build_cmd_line_parser()

    args = Config(cfg)
    args.merge_cfg(parser.parse_args())

    args.calculate()

    main(args)

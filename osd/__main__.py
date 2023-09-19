from __future__ import annotations

import pathlib
import sys
import time
from configparser import ConfigParser
from subprocess import Popen


from .utils.osd_props import detect_system, decode_fw_str
from .render import get_renderer
from .run_ffmpeg import run_ffmpeg_stdin
from .frame import Frame, SrtFrame
from .font import Font
from .const import CONFIG_FILE_NAME, OSD_TYPE_DJI
from .config import Config
from .utils.find_slot import find_slots
from .utils.video_props import get_video_properties
from .utils.srt import read_srt_frames
from .cmd_line import build_cmd_line_parser
from .dji import read_dji_osd_frames
from .ws import read_ws_osd_frames


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

    video_props = get_video_properties(video_path)
    args.update_narrow(video_props.width, video_props.height)

    print(f"verbatim:  {args.verbatim}")
    print(f"loading OSD dump from:  {osd_path}")

    if args.verbatim:
        print(f'Source video: {video_props.width}x{video_props.height} {video_props.fps}fps')

    osd_type, firmware = detect_system(osd_path)

    srt_frames = []
    if srt_exists:
        srt_frames = read_srt_frames(srt_path, args.verbatim, video_props.fps)

    if osd_type == OSD_TYPE_DJI:
        frames = read_dji_osd_frames(osd_path, args.verbatim, args)
    else:
        frames = read_ws_osd_frames(osd_path, args.verbatim, args)

    print(f"loading fonts from: {args.font}")
    system_name = decode_fw_str(firmware)
    hd = '_hd' if args.hd else ''
    font_file_name = pathlib.Path(args.font) / f'font_{system_name}{hd}'

    font = Font(font_file_name, args.hd, small_font_scale=args.srt_font_scale)

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

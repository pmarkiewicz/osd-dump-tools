import pathlib
import sys
from subprocess import Popen, PIPE

import ffmpeg

from .config import Config
from .utils.codecs import find_codec


def run_ffmpeg_stdin(cfg: Config, video_path: pathlib.Path, out_path: pathlib.Path, console: bool = False) -> Popen[bytes]:
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

    if cfg.hq:
        output_params.update(hq_output)

    cmd = video.filter("scale", **out_size, force_original_aspect_ratio=1) \
        .filter("pad", **out_size, x=-1, y=-1, color="black") \
        .overlay(frame_overlay, x=0, y=0) \
        .output(str(out_path), **output_params) \
        .global_args('-loglevel', 'info' if cfg.ffmpeg_verbatim else 'error') \
        .global_args('-stats') \
        .global_args('-hide_banner') \
        .overwrite_output() \
        .compile()

    if console:
        return Popen(cmd, stdin=PIPE)
    
    return Popen(cmd, stdin=PIPE, stderr=PIPE, bufsize=0, text=False)

    return video.filter("scale", **out_size, force_original_aspect_ratio=1) \
        .filter("pad", **out_size, x=-1, y=-1, color="black") \
        .overlay(frame_overlay, x=0, y=0) \
        .output(str(out_path), **output_params) \
        .global_args('-loglevel', 'info' if cfg.ffmpeg_verbatim else 'error') \
        .global_args('-stats') \
        .global_args('-hide_banner') \
        .overwrite_output() \
        .run_async(pipe_stdin=True, pipe_stderr=True, pipe_stdout=False, bufsize=0)

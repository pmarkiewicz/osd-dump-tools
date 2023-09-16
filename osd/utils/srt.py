import pathlib
from ..frame import SrtFrame
import re

import pysrt

from .time_to_ms import time_to_milliseconds


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

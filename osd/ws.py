import struct
import pathlib

from .config import Config
from .frame import Frame
from .ws_file_header import WSFileHeader

WS_VIDEO_FPS: int = 60

file_header_struct_ws = struct.Struct("<4s32B1H1H")
# < little-endian
# 4s string
# 32B unsigned char
# 2H unsigned short
# 2H unsigned short

frame_header_struct_ws = struct.Struct("<L1060H")
# < little-endian
# L unsigned long
# 1060H unsigned short


def read_ws_osd_header(osd_path: pathlib.Path) -> WSFileHeader:
    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_ws.size)
        file_header = file_header_struct_ws.unpack(file_header_data)

    return WSFileHeader(file_header)


def read_ws_osd_frames(osd_path: pathlib.Path, verbatim: bool, cfg: Config) -> list[Frame]:
    frames_per_ms = (1 / WS_VIDEO_FPS) * 1000
    frames: list[Frame] = []

    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_ws.size)
        file_header = file_header_struct_ws.unpack(file_header_data)
        ws_file_header = WSFileHeader(file_header)

        cfg.update_from_ws(ws_file_header)

        if verbatim:
            print(f"system:      {ws_file_header.system}")
            print(f"char width:  {ws_file_header.char_width}")
            print(f"char height: {ws_file_header.char_height}")

        while True:
            frame_header = dump_f.read(frame_header_struct_ws.size)
            if len(frame_header) == 0:
                break

            frame = frame_header_struct_ws.unpack(frame_header)
            osd_time = frame[0]
            frame_idx = int(osd_time // frames_per_ms)
            frame_data = frame[1:]

            if len(frames) > 0 and frames[-1].idx == frame_idx:
                if verbatim:
                    print(f'Duplicate frame: {frame_idx}')
                continue

            if len(frames) > 0:
                frames[-1].next_idx = frame_idx

            frames.append(Frame(frame_idx, 0, frame_header_struct_ws.size, frame_data))

    return frames

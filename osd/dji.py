import struct
import pathlib

from .config import Config
from .dji_file_header import DJIFileHeader
from .frame import Frame

MIN_START_FRAME_NO: int = 20
MAX_FRAME_SIZE: int = 2048

file_header_struct_dji = struct.Struct("<7sH4B2HB") 
# < little-endian
# 7s string
# H unsigned short
# 4B unsigned char
# 2H unsigned short
# B unsigned char
frame_header_struct_dji = struct.Struct("<II")
# < little-endian
# I unsigned int
# I unsigned int


def _get_min_frame_idx(frames: list[Frame]) -> int:
    # frames idxes are in increasing order for most of time :)

    for i in range(len(frames)):
        n1 = frames[i].idx
        n2 = frames[i+1].idx
        if n1 < n2:
            return n1

    raise ValueError("Frames are in wrong order")


def read_dji_osd_header(osd_path: pathlib.Path) -> DJIFileHeader:
    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_dji.size)
        file_header = file_header_struct_dji.unpack(file_header_data)
        
    return DJIFileHeader(file_header)


def read_dji_osd_frames(osd_path: pathlib.Path, verbatim: bool, cfg: Config) -> list[Frame]:
    frames: list[Frame] = []

    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_dji.size)
        file_header = file_header_struct_dji.unpack(file_header_data)
        dji_file_header = DJIFileHeader(file_header)

        cfg.update_from_dji(dji_file_header)

        if verbatim:
            print(f"file header:    {dji_file_header.file_header}")
            print(f"file version:   {dji_file_header.file_version}")
            print(f"char width:     {dji_file_header.char_width}")
            print(f"char height:    {dji_file_header.char_height}")
            print(f"font widtht:    {dji_file_header.font_width}")
            print(f"font height:    {dji_file_header.font_height}")
            print(f"x offset:       {dji_file_header.x_offset}")
            print(f"y offset:       {dji_file_header.y_offset}")
            print(f"font variant:   {dji_file_header.font_variant}")

        while True:
            frame_header = dump_f.read(frame_header_struct_dji.size)
            if len(frame_header) == 0:
                break

            frame_head = frame_header_struct_dji.unpack(frame_header)
            frame_idx, frame_size = frame_head

            if frame_size > MAX_FRAME_SIZE:
                print(f'Corrupted data, not all frames read. Frame size: {frame_size}. Last frame read: {frames[-1].idx}')
                break

            frame_data_struct = struct.Struct(f"<{frame_size}H")
            frame_data = dump_f.read(frame_data_struct.size)
            if len(frame_data) != frame_data_struct.size:
                print(f'Corrupted data, not all frames read. Frame size: {frame_size}. Last frame read: {frames[-1].idx}')
                break

            frame_data = frame_data_struct.unpack(frame_data)
            if len(frames) > 0 and frames[-1].idx == frame_idx:
                if verbatim:
                    print(f'Duplicate frame: {frame_idx}')
                continue

            if len(frames) > 0:
                frames[-1].next_idx = frame_idx

            frames.append(Frame(frame_idx, 0, frame_size, frame_data))

    # remove initial random frames
    start_frame = _get_min_frame_idx(frames)

    if start_frame > MIN_START_FRAME_NO:
        print(f'Wrong idx of initial frame {start_frame}, abort')
        raise ValueError(f'Wrong idx of initial frame {start_frame}, abort')

    frames = frames[start_frame:]
    zero_frame = []
    if start_frame > 0:
        zero_frame = [Frame(0, frames[0].idx, 0, None)]

    return zero_frame + frames

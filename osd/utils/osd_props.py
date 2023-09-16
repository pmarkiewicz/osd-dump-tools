import struct
import pathlib

from ..const import OSD_TYPE_DJI, OSD_TYPE_WS, FW_ARDU, FW_INAV, FW_BETAFL
from ..dji import read_dji_osd_header


file_header_struct_detect = struct.Struct("<4s")
# < little-endian
# 4s string


def detect_system(osd_path: pathlib.Path, verbatim: bool = False) -> tuple :
    with open(osd_path, "rb") as dump_f:
        file_header_data = dump_f.read(file_header_struct_detect.size)
        file_header = file_header_struct_detect.unpack(file_header_data)

    if file_header[0] == b'MSPO':
        dji_file_header = read_dji_osd_header(osd_path)
        if dji_file_header.font_variant == 1:   # TODO: change to const, what about BF?
            return OSD_TYPE_DJI, FW_BETAFL
        if dji_file_header.font_variant == 2:   # TODO: change to const, what about BF?
            return OSD_TYPE_DJI, FW_INAV
        if dji_file_header.font_variant == 3:   # TODO: change to const, what about BF?
            return OSD_TYPE_DJI, FW_ARDU
    
    if file_header[0] == b'INAV':
        return OSD_TYPE_WS, FW_INAV
    if file_header[0] == b'BTFL':
        return OSD_TYPE_WS, FW_BETAFL
    if file_header[0] == b'ARDU':
        return OSD_TYPE_WS, FW_ARDU

    print(f"{osd_path} has an invalid file header")
    sys.exit(1)


def decode_system_str(firmware: int) -> str:
    if firmware == FW_BETAFL:
        return 'bf'
    
    if firmware == FW_ARDU:
        return 'ardu'
    
    return 'inav'

from threading import Thread
import time
import subprocess
import platform
from collections import namedtuple
from typing import List

CodecDef = namedtuple("CodecDev", "codec os")


def _find_codec(codecs: List[CodecDef], os: str) -> bool:
    # code borrowed from ws-osd
    #
    cmd_line = "ffmpeg -y -hwaccel auto -f lavfi -i nullsrc -c:v {0} -frames:v 1 -f null -"
    for codec in (codec.codec for codec in codecs if os in codec.os):
        cmd = (cmd_line.format(codec)).split(" ")
        ret = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if ret.returncode == 0:
            return codec

    return None


def find_codec(use_h265: bool) -> str | None:
    codecs_h265 = [
        CodecDef("h265_videotoolbox", ("darwin")),
        CodecDef("hevc_nvenc", ("windows", "linux")),
        CodecDef("hevc_amf", ("windows")),
        CodecDef("hevc_qsv", ("windows", "linux")),
        CodecDef("hevc_mf", ("windows")),
        CodecDef("libx265", ("darwin", "windows", "linux")),
    ]

    codecs_h264 = [
        CodecDef("h264_videotoolbox", ("darwin")),
        CodecDef("h264_nvenc", ("windows", "linux")),
        CodecDef("h264_amf", ("windows")),
        CodecDef("h264_vaapi", ("linux")),
        CodecDef("h264_qsv", ("windows", "linux")),
        CodecDef("h264_mf", ("windows")),
        CodecDef("h264_v4l2m2m", ("linux")),
        CodecDef("libx264", ("darwin", "windows", "linux")),
    ]

    os = platform.system().lower()

    if use_h265:
        codec = _find_codec(codecs_h265, os)
        if codec:
            return codec
    
    return _find_codec(codecs_h264, os)

    return None


def _find_codec_bkgnd(callback: callable, use_h265: bool):
    codec = find_codec(use_h265)
    callback(codec)


def find_codec_bknd(callback: callable, use_h265: bool) -> str | None:
    th = Thread(target=_find_codec_bkgnd, args=(callback, use_h265,))
    th.start()
    time.sleep(0)

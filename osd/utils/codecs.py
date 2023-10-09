from threading import Thread
import time
import subprocess
import platform
from collections import namedtuple


def find_codec() -> str | None:    
    # code borrowed from ws-osd
    #     
    CodecDef = namedtuple('CodecDev', 'codec os')

    codecs = [CodecDef('h264_videotoolbox', ('darwin')), 
              CodecDef('h264_nvenc', ('windows', 'linux')), 
              CodecDef('h264_amf', ('windows')),
              CodecDef('h264_vaapi', ('linux')), 
              CodecDef('h264_qsv', ('windows', 'linux')),
              CodecDef('h264_mf', ('windows')),
              CodecDef('h264_v4l2m2m', ('linux')), 
              CodecDef('libx264', ('darwin', 'windows', 'linux')),
             ]

    cmd_line = 'ffmpeg -y -hwaccel auto -f lavfi -i nullsrc -c:v {0} -frames:v 1 -f null -'

    os = platform.system().lower()
    for codec in (codec.codec for codec in codecs if os in codec.os):
        cmd = (cmd_line.format(codec)).split(" ")
        ret = subprocess.run(cmd, 
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)

        if ret.returncode == 0:
            return codec

    return None


def _find_codec_bkgnd(callback: callable):
    codec = find_codec()
    callback(codec)


def find_codec_bknd(callback: callable) -> str | None:
    th = Thread(target=_find_codec_bkgnd, args=(callback, ))
    th.start()
    time.sleep(0)

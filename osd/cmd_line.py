import argparse


def build_cmd_line_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("video", type=str, help="video file e.g. DJIG0007.mp4")
    parser.add_argument(
        "--font", type=str, default=None, help='folder where are all font files (inav, ardu, bf)'
    )
    parser.add_argument(
        "--bitrate", type=int, default=None, help='output bitrate'
    )
    parser.add_argument(
        "--max_alt", type=int, default=None, help='max displayed altitude if --hide_alt is enbled, default 0'
    )
    parser.add_argument(
        "--out_resolution", type=str, default=None, choices=['hd', 'fhd', '2k'], help="output resolution hd is 720 lines, fhd is 1080, 2k is 1440, default is fhd"
    )

    parser.add_argument(
        "--hq", action="store_true", default=None, help="render with high quality profile (slower)"
    )

    parser.add_argument(
        "--hide_gps", action="store_true", default=None, help="Don't render GPS coords."
    )

    parser.add_argument(
        "--hide_alt", action="store_true", default=None, help="Don't render altitude."
    )

    parser.add_argument(
        "--hide_dist", action="store_true", default=None, help="Don't render distance from home."
    )

    parser.add_argument(
        "--testrun", action="store_true", default=False, help="Create overlay with osd data in video location and ends"
    )

    parser.add_argument(
        "--testframe", type=int, default=-1, help="Osd data frame for testrun"
    )

    parser.add_argument(
        "--verbatim", action="store_true", default=None, help="Display detailed information"
    )

    parser.add_argument(
        "--ffmpeg_verbatim", action="store_true", default=None, help="Display detailed information from ffmpeg"
    )

    parser.add_argument(
        "--srt", type=str, default=None, help='Display information from srt file, list separated by :, signal:ch:delay:bitrate'
    )

    parser.add_argument(
        "--overlay", type=str, default=None, help='Overlay image, parameters are comma separated x,y,img like 10,100,resources\inav_icon_128.png'
    )

    return parser

import argparse
from .config import ExcludeArea


def build_cmd_line_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    parser.add_argument("video", type=str, help="video file e.g. DJIG0007.mp4")
    parser.add_argument(
        "--font", type=str, default=None, help='font basename e.g. "font"'
    )
    parser.add_argument(
        "--bitrate", type=int, default=None, help='output bitrate'
    )
    parser.add_argument(
        "--ignore_area", type=ExcludeArea, nargs='*', default="-1, -1, 0, 0", help="don't display area (in fonts, x1,y1,x2,y2), i.e. 10,10,15,15, can be repeated"
    )

    parser.add_argument(
        "--out_resolution", type=str, default=None, choices=['hd', 'fhd', '2k'], help="output resolution hd is 720 lines, fhd is 1080, 2k is 1440, default is fhd"
    )

    parser.add_argument(
        "--narrow", action="store_true", default=None, help="use 4:3 proportions instead of default 16:9"
    )

    parser.add_argument(
        "--nolinks", action="store_true", default=None, help="Copy frames instead of linking (windows without priviledged shell)"
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
        "--singlecore", action="store_true", default=None, help="Run on single procesor core (slow)"
    )

    parser.add_argument(
        "--ardu", action="store_true", default=None, help="Hide gps/alt/distance for ArduPilot"
    )

    parser.add_argument(
        "--osd_resolution", type=str, default='60x22', help='OSD resolution, default is 60x22, other popular are: "50x18" and "30x16"'
    )

    parser.add_argument(
        "--srt", type=str, default=None, help='Display information from srt file, list separated by :, signal:ch:delay:bitrate'
    )

    return parser

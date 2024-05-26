# Intro
osd-tool let you create overlay on video recorded from dji wtfos or walksnail avatar.
Let's you control visibility of distance, gps location and altitude (you can let limit), can also hide stats at end of flight.
Can display additional information like signal, channel, bitrate and delay.
Works with ardupilot, iNav and betaflight.
Works on windows, macos and linux

There is also command line if you need to batch convert.

# How to run
Make sure that you have ffmpeg installed
and simply use on windows
```
run.cmd 
```
# gui added

After installation as described below just use run.cmd on windows to start program.
GUI is simple, not very well tested now and requires improvement.

# osd-dump tools

Updated version, no more files saved on disk, everything is in memory.

Overlays dji and walksnail recordings over video files with data from srt files.
Walksnail is decoded automatically and rendered as full hd, same fonts as for dji are used.

### Requirements

- Windows as described below or [use WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
- Python 3.11+ is required.
- ffmpeg is required.

  ```shell
  # Debian and friends
  $ sudo apt install ffmpeg

  # macOS
  $ brew install ffmpeg
  ```

  # Windows
  Download ffmpeg from https://github.com/BtbN/FFmpeg-Builds/releases
  Extract to any folder on disk (i.e. c:\ffmpeg), add this folder to environment variable 'path'. 
### Setup

```shell
# Setting up a virtual environment is recommended, but not required.
# on linux, wsl or macos
python -m venv venv
source ./venv/bin/activate

# on windows
python -m venv venv
venv/scripts/activate

# Install dependencies.
$ pip install -r requirements.txt
```

### Usage

- Place font files in standard directory and use --font to set fonts location. Osd and video files should be in same directory.

```shell
# Check out the options.
$ python -m osd --help

  usage: __main__.py [-h] [--font FONT] video

  positional arguments:
    video        video file e.g. DJIG0007.mp4

  options:
    -h, --help    show this help message and exit
    --font folder   folder where are all font files (inav, ardu, bf)
    --bitrate     output bitrate, default is 25mbps
    --out_resolution [hd, fhd, 2k]  output resolution hd is 720 lines, fhd is 1080, 2k is 1440, default is fhd
    --hq              render output files with high quality as described in [FFMPEG FAQ](https://ffmpeg.org/faq.html#Which-are-good-parameters-for-encoding-high-quality-MPEG_002d4_003f)
    --hide_gps        automatically hides gps coordinates from video
    --hide_alt        automatically hides altitude
    --hide_dist       automatically hides distance from home
    --testrun         creates overlay image in video directory, ignoread areas are marked with X
    --testframe       use frame no from osd file to test data, useful if default frame displays something else than normal osd (like flight summary)
    --verbatim        display detailed information
    --ardu            necessary to hide gps/alt/dist for ArduPilot
    --osd_resolution  OSD resolution, default is 60x22, other popular are: "50x18" and "30x16"
    --srt             Display information from srt file, list separated by :, i.e. signal:ch:delay:bitrate

# Config file
All parameters can be set in ini file located in osd folder. Parameters can be overriden by ini file in current directory.

# Convert your recording!
Run run.cmd and all settings are in UI
```

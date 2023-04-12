# osd-dump tools

Overlays msp-osd and walksnail recordings over video files.
Walksnail is decoded automatically and rendered as full hd, same fonts as for dji are used.
At this moment different firmwares doesn't select proper fonts. 
Current walksnail limitation is only 60fps and anly full hd.

### Requirements

- Windows as described below or [use WSL](https://learn.microsoft.com/en-us/windows/wsl/install).
- Python 3.8+ is required.
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
  To use links you have to run elevated cmd. (Start-> search for cmd -> right click -> run as admin.)
  If you don't like to use elevated shell you can use --nolinks option other solution is to use WSL.
  --nolinks option consume more disk space as instead of linking files there are saved on disk.
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
    --font FONT   font basename e.g. "font"
    --hd          is this an HD OSD recording?
    --fakehd      are you using fakehd?
    --bitrate     output bitrate, default is 25mbps
    --ignore_area very useful option to hide GPS coords or altitude, can be repeated, parameters are top,left,right,bottom i.e. '--ignore_area 5,5,15,15 3,3,5,5'
    --nolinks     instead on linking exising files full copy is saved
    --hq          render output files with high quality as described in [FFMPEG FAQ](https://ffmpeg.org/faq.html#Which-are-good-parameters-for-encoding-high-quality-MPEG_002d4_003f)
    --testrun     creates overlay image in video directory, very useful to test --ignore_area option, ignoread areas are marked with X
    --testframe   use frame no from osd file to test data, useful if default frame displays something else than normal osd (like flight summary)
    --hide_gps    automatically hides gps coordinates from video
    --hide_alt    automatically hides altitude
    --hide_dist   automatically hides distance from home
    --verbatim    display detailed information
    --singlecore  run on single procesor core (slow)
    --ardu        necessary to hide gps/alt/dist for ArduPilot
    --ardu-legacy use legacy resolution 50x18 for ArduPilot
    --out_resolution [hd, fhd, 2k]  output resolution hd is 720 lines, fhd is 1080, 2k is 1440, default is fhd
    

# Config file
All parameters can be set in ini file located in osd folder. Parameters can be overriden by ini file in current directory.

# Convert your recording!
$ python -m osd --font font_inav --hd  DJIG0001.mp4

  INFO:__main__:loading OSD dump from DJIG0001.osd
  INFO:__main__:rendering 168 frames
  INFO:__main__:passing to ffmpeg, out as DJIG0001_with_osd.mp4
  ... etc ...
```

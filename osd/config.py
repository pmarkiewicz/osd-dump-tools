from __future__ import annotations

import argparse
import pathlib
import sys
from configparser import ConfigParser
from PIL import Image, UnidentifiedImageError
from .const import DEFAULT_SECTION, SD_RESOLUTION_LIMIT, MAX_DISPLAY_X, MAX_DISPLAY_Y, FW_ARDU, HD_TILE_WIDTH
from .dji_file_header import DJIFileHeader
from .ws_file_header import WSFileHeader


class Config:
    params: tuple[tuple[str, type]] = (
        ('font', str), ('bitrate', int), ('ffmpeg_verbatim', bool),
        ('testrun', bool), ('testframe', int), ('hq', bool),
        ('hide_gps', bool), ('hide_alt', bool), ('hide_dist', bool), ('verbatim', bool),
        ('ardu', bool), ('overlay', str),
        ('out_resolution', str), 
        ('osd_resolution', str), ('srt', str),
    )

    def __init__(self, cfg: ConfigParser):
        super().__init__()

        self.font : str = ''
        self.bitrate: int = 25
        self.out_resolution: str = 'fhd'
        self.narrow: bool = False
        self.hq: bool = False
        self.hide_gps: bool = False
        self.hide_alt: bool = False
        self.hide_dist: bool = False
        self.testrun: bool = False
        self.testframe: int = -1
        self.verbatim: bool = False
        self.ffmpeg_verbatim: bool = False
        self.ardu: bool = False
        self.osd_resolution: str = '60x22'
        self.srt = ''
        self.overlay = None

        self.hd: bool = True
        self.display_width: int = -1
        self.display_height: int = -1
        self.overlay_location = None
        self.overlay_img = None
        self.srt_data = []
        self.srt_font_scale = 0.7
        self.srt_start_location = (1, -1,)
        self.srt_fmt = {
            'signal': '\x27{:n}',
            'ch': 'CH:{:n}',
            'delay': 'D:{:n}MS',
            'bitrate': 'BR:{:.1f}',
        }

        self.update_cfg(cfg[DEFAULT_SECTION])

    def set_value_from_cfg(self, cfg: ConfigParser, name: str, t: type) -> None:
        try:
            v = cfg[name]
            if t == bool:   # we need special handling
                v = v.lower() not in ('false', 'no', '0')
                
            setattr(self, name, t(v))
        except KeyError:
            pass

    def update_cfg(self, cfg) -> None:
        for name, typ in self.params:
            self.set_value_from_cfg(cfg, name, typ)

    def merge_cfg(self, args: argparse.Namespace) -> None:
        for name, typ in self.params:
            v = getattr(args, name, None)
            if v is not None:
                setattr(self, name, v)

        # this is special case
        self.video = args.video

    def _calculate_video_resolution(self):
        out_resolution = self.out_resolution.lower()

        if out_resolution == 'hd':
            self.target_height = 720
        elif out_resolution == 'fhd':
            self.target_height = 1080
        elif out_resolution == '2k':
            self.target_height = 1440
        else:
            print(f'Parameter out_resolution is incorrect: "{self.out_resolution}"')
            sys.exit(2)

        if self.narrow:
            self.target_width = (self.target_height * 4) // 3
        else:
            self.target_width = (self.target_height * 16) // 9

    def _calculate_osd_resolution(self):
        dims = self.osd_resolution.split('x')
        if len(dims) != 2:
            print(f'Parameter osd_resolution has incorrect format: "{self.osd_resolution}"')
            sys.exit(2)

        try:
            self.display_width = int(dims[0])
            self.display_height = int(dims[1])
        except ValueError:
            print(f'Parameter osd_resolution has incorrect value: "{self.osd_resolution}"')
            sys.exit(3)

        if self.display_width > MAX_DISPLAY_X:
            print(f'Parameter width {self.display_width} for osd_resolution is too big, limit is: "{MAX_DISPLAY_X}"')
            sys.exit(4)

        if self.display_height > MAX_DISPLAY_Y:
            print(f'Parameter width {self.display_height} for osd_resolution is too big, limit is: "{MAX_DISPLAY_Y}"')
            sys.exit(4)

        self.hd = self.display_width > SD_RESOLUTION_LIMIT

    def _update_srt(self):
        if self.srt:
            items = self.srt.split(':')
            self.srt_data = items

    def _update_overlay(self):
        if self.overlay:
            parts = self.overlay.split(',')
            if len(parts) != 3:
                print('Incorrect no of params for overlay')
                sys.exit(4)

            try:
                x = int(parts[0].strip())
                y = int(parts[1].strip())
            except ValueError:
                print('Incorrect overlay coordinates')
                sys.exit(4)

            img_path = pathlib.Path(parts[2])
            if not img_path.exists():
                print(f'Overlay file "{img_path}" does not exists. Terminating.')
                sys.exit(4)

            try:
                img = Image.open(img_path)
            except UnidentifiedImageError:
                print(f'Unrecognised image {img_path}')
                sys.exit(4)

            # if x < 0:
            #     x = self.target_width + x * img.width
            # if y < 0:
            #     y = self.target_height + y * img.width

            self.overlay_img = img
            self.overlay_location = (x, y,)

    def calculate(self):
        """
        Calculate config parameters based on other values
        """
        self._calculate_video_resolution()
        self._calculate_osd_resolution()
        self._update_srt()
        self._update_overlay()

    def update_from_dji(self, dji_file_header: DJIFileHeader) -> None:
        self.display_width = dji_file_header.char_width
        self.display_height = dji_file_header.char_height
        self.hd = dji_file_header.font_width == HD_TILE_WIDTH

        if dji_file_header.font_variant == FW_ARDU:
            self.ardu = True

    def update_from_ws(self, ws_file_header: WSFileHeader) -> None:
        self.display_width = ws_file_header.char_width
        self.display_height = ws_file_header.char_height

        if ws_file_header.system == 'ARDU':
            self.ardu = True

    def update_narrow(self, width: int, height: int) -> None:
        if (height / width) == 0.75:
            self.narrow = True

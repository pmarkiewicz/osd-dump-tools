from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from configparser import ConfigParser
from .const import DEFAULT_SECTION, SD_RESOLUTION_LIMIT, MAX_DISPLAY_X, MAX_DISPLAY_Y


class ExcludeArea:
    def __init__(self, s: str = None):

        if not s:
            self.x1 = -1
            self.y1 = -1
            self.x2 = -1
            self.y2 = -1

            return

        nums = s.split(',')
        if len(nums) != 4:
            raise ValueError('Incorrect no of region parameters, should be 4, received {len(nums)}.')

        self.x1 = int(nums[0])
        self.y1 = int(nums[1])
        self.x2 = int(nums[2])
        self.y2 = int(nums[3])

    def is_excluded(self, x: int, y: int) -> bool:
        return self.x1 <= x < self.x2 and self.y1 <= y < self.y2


class MultiExcludedAreas:
    def __init__(self):
        self.excluded_areas = []

    def is_excluded(self, x: int, y: int) -> bool:
        for area in self.excluded_areas:
            if area.is_excluded(x, y):
                return True

        return False

    def merge(self, params: ExcludeArea | list[ExcludeArea]) -> None :
        try:
            for area in params:
                self.excluded_areas.append(area)
        except TypeError:
            self.excluded_areas.append(params)


class Config:
    params: tuple[tuple[str, type]] = (
        ('font', str), ('bitrate', int),
        ('testrun', bool), ('testframe', int), ('hq', bool),
        ('hide_gps', bool), ('hide_alt', bool), ('hide_dist', bool), ('verbatim', bool),
        ('ardu', bool), 
        ('out_resolution', str), ('narrow', bool),
        ('osd_resolution', str), ('srt', str),
    )

    def __init__(self, cfg: ConfigParser):
        super().__init__()

        self.font : str = ''
        self.bitrate: int = 25
        self.testrun: bool = False
        self.testframe: int = -1
        self.hq: bool = False
        self.hide_gps: bool = False
        self.hide_alt: bool = False
        self.hide_dist: bool = False
        self.verbatim: bool = False
        self.ardu: bool = False
        self.ardu_legacy: bool = False
        self.out_resolution: str = 'fhd'
        self.narrow: bool = False
        self.osd_resolution: str = '60x22'
        self.srt = ''

        self.hd: bool = True
        self.display_width: int = -1
        self.display_height: int = -1
        self.srt_data = []
        self.srt_font_scale = 0.7
        self.srt_start_location = (1, -1,)
        self.srt_fmt = {
            'signal': '\x27{:n}',
            'ch': 'CH:{:n}',
            'delay': 'D:{:n}MS',
            'bitrate': 'BR:{:.1f}',
        }

        self.exclude_area = MultiExcludedAreas()

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

        # update regions
        for i in range(1, 100):
            try:
                val = cfg[f'ignore_area_{i}']
                self.exclude_area.merge(ExcludeArea(val))
            except KeyError:
                break

    def merge_cfg(self, args: argparse.Namespace) -> None:
        for name, typ in self.params:
            v = getattr(args, name, None)
            if v is not None:
                setattr(self, name, v)

        # this is special case
        self.video = args.video

        # and another special case
        if self.ardu_legacy:
            self.ardu = True

        # merge regions
        self.exclude_area.merge(args.ignore_area)

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

    def calculate(self):
        """
        Calculate config parameters based on other values
        """
        self._calculate_video_resolution()
        self._calculate_osd_resolution()
        self._update_srt()

from __future__ import annotations

import argparse
from configparser import ConfigParser
from .const import DEFAULT_SECTION



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
        ('font', str), ('hd', bool), ('fakehd', bool), ('bitrate', int),
        ('nolinks', bool), ('testrun', bool), ('testframe', int), ('hq', bool),
        ('hide_gps', bool), ('hide_alt', bool), ('hide_dist', bool), ('verbatim', bool),
        ('singlecore', bool), ('ardu', bool), ('ardu_legacy', bool), 
        ('out_resolution', str), ('narrow', bool),
    )

    def __init__(self, cfg: ConfigParser):
        super().__init__()

        self.font : str = ''
        self.fakehd: bool = False
        self.bitrate: int = 25
        self.nolinks: bool = False
        self.testrun: bool = False
        self.testframe: int = -1
        self.hd: bool = True
        self.hq: bool = False
        self.hide_gps: bool = False
        self.hide_alt: bool = False
        self.hide_dist: bool = False
        self.verbatim: bool = False
        self.singlecore: bool = False
        self.ardu: bool = False
        self.ardu_legacy: bool = False
        self.out_resolution: str
        self.narrow: bool = False

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

    def calculate(self):
        out_resolution = self.out_resolution.lower()

        if out_resolution == 'hd':
            self.height = 720
        elif out_resolution == 'fhd':
            self.height = 1080
        else:
            self.height = 1440

        if self.narrow:
            self.width = (self.height * 4) // 3
        else:
            self.width = (self.height * 16) // 9

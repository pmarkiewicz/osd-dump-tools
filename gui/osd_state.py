import pathlib
from typing import Callable
from dataclasses import dataclass
from configparser import ConfigParser

import flet as ft

from osd.config import Config
from osd.const import OSD_TYPE_DJI, DEFAULT_SECTION, CONFIG_FILE_NAME
from osd.frame import Frame, SrtFrame
from osd.font import Font
from osd.dji import read_dji_osd_frames
from osd.ws import read_ws_osd_frames
from osd.utils.video_props import VideoProperties, get_video_properties
from osd.utils.osd_props import detect_system, decode_fw_str, decode_system_str
from osd.utils.srt import read_srt_frames

from .utils import cut_path


@dataclass
class OsdState:
    page: ft.Page = None
    cfg: Config = None
    error_handler = ft.AlertDialog = None
    osd_type: int = None
    frames: list[Frame] = None
    srt_frames: list[SrtFrame] = None
    fw_name: str = None
    video_props: VideoProperties = None
    font: Font = None
    osd_name: str = None
    _video_path: pathlib.Path = None
    _osd_path: pathlib.Path = None
    _srt_path: pathlib.Path = None
    _out_path: pathlib.Path = None

    is_render_ready: bool = False

    def __post_init__(self):
        pass

    def reset(self):
        self.osd_type: int = None
        self.frames: list[Frame] = None
        self.srt_frames: list[SrtFrame] = None
        self.fw_name: str = None
        self.video_props: VideoProperties = None
        self.font: Font = None
        self.osd_name: str = None
        self._video_path: pathlib.Path = None
        self._osd_path: pathlib.Path = None
        self._srt_path: pathlib.Path = None
        self._out_path: pathlib.Path = None
        
    def font_load(self, path: str) -> None:
        self.cfg.font = path
        self._load_font()

    def _load_font(self):
        if self.fw_name and self.cfg.font:
            hd = '_hd' if self.cfg.hd else ''
            font_file_name = pathlib.Path(self.cfg.font) / f'font_{self.fw_name}{hd}'

            try:
                self.font = Font(font_file_name, self.cfg.hd, small_font_scale=self.cfg.srt_font_scale)
            except FileNotFoundError:
                self.error_handler(f'Font file does not exisit "{cut_path(font_file_name)}"')

            self.page.pubsub.send_all_on_topic('font', f'Font loaded {cut_path(font_file_name)}')
            self.update_ready()
            self.update_ini()

            return

        self.page.pubsub.send_all_on_topic('font', 'Font not loaded')
        self.update_ready()

    def video_load(self, path: str) -> None:
        self._video_path = pathlib.Path(path)
        video_stem = self._video_path.stem
        self._osd_path = self._video_path.with_suffix('.osd')
        self._srt_path = self._video_path.with_suffix('.srt')
        self._out_path = self._video_path.with_name(video_stem + "_with_osd.mp4")

        self.update_video_info()
        self.update_osd_info()
        self.update_srt_info()

        self.update_ready()

    def update_srt_info(self):
        if not self._srt_path.exists():
            self.page.pubsub.send_all_on_topic('srt loaded', 'Srt not loaded')
            self._srt_path = ''
        else:
            self.read_srt_frames()
            self.page.pubsub.send_all_on_topic('srt loaded', f'Srt loaded {len(self.srt_frames)} frames')
            self.update_ready()

    def update_osd_info(self):
        if not self._osd_path.exists():
            self.page.pubsub.send_all_on_topic('osd loaded', 'not loaded')
        else:
            self.detect_system()
            self.read_osd_frames()
            self._load_font()
            self.page.pubsub.send_all_on_topic('osd loaded', f'System: {self.osd_name}, fw: {self.fw_name}, loaded {len(self.frames)} osd frames')
            self.update_ready()

    def update_video_info(self):
        self.video_props = get_video_properties(self._video_path)
        video_info = f'Source video: {self.video_props.width}x{self.video_props.height} {self.video_props.fps}fps {self.video_props.duration_min}:{self.video_props.duration_sec}'
        self.page.pubsub.send_all_on_topic('video loaded', video_info)
        self.update_ready()

    def update_out_info(self):
        self.update_ready()

    def detect_system(self):
        self.osd_type, firmware = detect_system(self._osd_path)
        self.fw_name = decode_fw_str(firmware)
        self.osd_name = decode_system_str(self.osd_type)

    def update_ready(self):
        self.is_render_ready = self.frames and self.font and self.video_props

    def read_srt_frames(self):
        self.srt_frames = read_srt_frames(self._srt_path, False, self.video_props.fps)        

    def read_osd_frames(self):
        if self.osd_type == OSD_TYPE_DJI:
            self.frames = read_dji_osd_frames(self._osd_path, False, self.cfg)
        else:
            self.frames = read_ws_osd_frames(self._osd_path, False, self.cfg)

    @property
    def video_resolution(self) -> tuple[int, int]:
        return (self.cfg.target_width, self.cfg.target_height, )

    @property
    def output_resolution(self) -> str:
        return self.cfg.out_resolution

    @output_resolution.setter
    def output_resolution(self, resolution: str) -> None:
        self.cfg.update_video_resolution(resolution)
        self.update_ini()

    @property
    def video_path(self) -> pathlib.Path:
        return self._video_path

    @video_path.setter
    def video_path(self, path: str | pathlib.Path):
        if isinstance(path, str):
            self._video_path = pathlib.Path(path)
        else:
            self._video_path = path

    @property
    def osd_path(self) -> pathlib.Path:
        return self._osd_path

    @osd_path.setter
    def osd_path(self, path: str | pathlib.Path):
        if isinstance(path, str):
            self._osd_path = pathlib.Path(path)
        else:
            self._osd_path = path

    @property
    def srt_path(self) -> pathlib.Path:
        return self._srt_path

    @srt_path.setter
    def srt_path(self, path: str | pathlib.Path):
        if isinstance(path, str):
            self._srt_path = pathlib.Path(path)
        else:
            self._srt_path = path

    @property
    def out_path(self) -> pathlib.Path:
        return self._out_path

    @out_path.setter
    def out_path(self, path: str | pathlib.Path):
        if isinstance(path, str):
            self._out_path = pathlib.Path(path)
        else:
            self._out_path = path

    @property
    def srt_data(self) -> list[str]:
        return self.cfg.srt_data

    @srt_data.setter
    def srt_data(self, value):
        self.cfg.srt_data = value
        self.update_ini()

    @property
    def hide_gps(self) -> bool:
        return self.cfg.hide_gps

    @hide_gps.setter
    def hide_gps(self, value: bool):
        self.cfg.hide_gps = value
        self.update_ini()

    @property
    def hide_alt(self) -> bool:
        return self.cfg.hide_alt

    @hide_alt.setter
    def hide_alt(self, value: bool):
        self.cfg.hide_alt = value
        self.update_ini()

    @property
    def hide_dist(self) -> bool:
        return self.cfg.hide_dist

    @hide_dist.setter
    def hide_dist(self, value: bool):
        self.cfg.hide_dist = value
        self.update_ini()

    @property
    def hq(self) -> bool:
        return self.cfg.hq

    @hq.setter
    def hq(self, value: bool):
        self.cfg.hq = value
        self.update_ini()

    @property
    def bitrate(self) -> bool:
        return self.cfg.bitrate

    @bitrate.setter
    def bitrate(self, value: int):
        self.cfg.bitrate = value
        self.update_ini()

    @property
    def srt_start_location(self) -> tuple[int, int]:
        return self.cfg.srt_start_location

    @srt_start_location.setter
    def srt_start_location(self, value: str):
        self.cfg.srt_start = value
        self.cfg.update_srt_start()
        self.update_ini()

    @property
    def font_folder(self) -> bool:
        return self.cfg.font

    def update_ini(self):
        config = {
            'hq': self.hq,
            'bitrate': self.bitrate,
            'font': self.font_folder,
            'hide_dist': self.hide_dist,
            'hide_alt': self.hide_alt,
            'hide_gps': self.hide_gps,
            'srt': ':'.join(self.srt_data),
            'srt_start': self.srt_start_location,
            'out_resolution': self.output_resolution,
        }
        parser = ConfigParser()
        parser.read_dict({DEFAULT_SECTION: config})

        with open(pathlib.Path.home() / CONFIG_FILE_NAME, 'w') as f:
            parser.write(f)


@dataclass
class Events:
    update: Callable = None
    render: Callable = None
    render_test_frame: Callable = None
    render_last_frame: Callable = None

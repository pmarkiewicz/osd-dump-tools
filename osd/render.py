from dataclasses import dataclass
from io import BytesIO
from PIL import Image

from .const import HD_TILE_WIDTH, SD_TILE_WIDTH, HD_TILE_HEIGHT, SD_TILE_HEIGHT, OSD_TYPE_DJI, ArduParams, InavParams
from .font import Font
from .frame import Frame, SrtFrame
from .config import Config

INTERNAL_W_H_DJI = (60, 22)
INTERNAL_W_H_WS = (53, 20)


@dataclass(slots=True)
class HiddenItemsCache():
    gps_lat: tuple[int, int] | None = None
    gps_lon: tuple[int, int] | None = None
    alt: tuple[int, int] | None = None
    dist: tuple[int, int] | None = None


class BaseRenderer:
    __slots__ = 'font', 'cfg', 'osd_type', 'frames', 'srt_frames', 'tile_width', 'tile_height', 'masking_tile', 'exclusions', 'display_width', 'display_height', 'final_img_size'

    def __init__(self, font: Font, cfg: Config, osd_type: int, frames: list[Frame], srt_frames: list[SrtFrame], reset_cache: bool = False) -> None:
        if reset_cache:
            self._items_cache = HiddenItemsCache()

        self.font = font
        self.cfg = cfg
        self.osd_type = osd_type
        self.frames = frames
        self.srt_frames = srt_frames
        self._items_cache = HiddenItemsCache()

        self.tile_width = HD_TILE_WIDTH
        self.tile_height = HD_TILE_HEIGHT 
        if not self.cfg.hd:
            self.tile_width = SD_TILE_WIDTH
            self.tile_height = SD_TILE_HEIGHT

        masking_font_no = ord(' ')
        if self.cfg.testrun:
            masking_font_no = ord('X')

        self.masking_tile = self.font[masking_font_no]

        self.exclusions = InavParams
        if self.cfg.ardu:
            self.exclusions = ArduParams

        self.display_width = self.cfg.display_width
        self.display_height = self.cfg.display_height

        self.final_img_size = (self.cfg.target_width, self.cfg.target_height)

        self.base_img = Image.new(
            "RGBA",
            (
                self.display_width  * self.tile_width,
                self.display_height * self.tile_height,
            ),
        )

        self.last_frame = Frame(0, 0, 0, [0] * (self.internal_height * self.internal_width))

    def hide_items(self) -> None:
        if self._items_cache.gps_lat:
            for i in range(self.exclusions.GPS_LEN + 1):
                x = (self._items_cache.gps_lat[0] + i) * self.tile_width
                y = self._items_cache.gps_lat[1] * self.tile_height
                self.base_img.paste(self.masking_tile, (x , y,), )

        if self._items_cache.gps_lon:
            for i in range(self.exclusions.GPS_LEN + 1):
                x = (self._items_cache.gps_lon[0] + i) * self.tile_width
                y = self._items_cache.gps_lon[1] * self.tile_height
                self.base_img.paste(self.masking_tile, (x , y,), )

        if self._items_cache.alt:
            for i in range(self.exclusions.ALT_LEN + 1):
                x = (self._items_cache.alt[0] - i) * self.tile_width
                y = self._items_cache.alt[1] * self.tile_height
                self.base_img.paste(self.masking_tile, (x , y,), )

        if self._items_cache.dist:
            for i in range(self.exclusions.HOME_LEN + 1):
                x = (self._items_cache.dist[0] + i) * self.tile_width
                y = self._items_cache.dist[1] * self.tile_height
                self.base_img.paste(self.masking_tile, (x , y,), )

    def draw_str(self, x: int, y: int, txt: str) -> None:
        tile_step = int(self.tile_width * self.cfg.srt_font_scale)
        for n, c in enumerate(txt):
            tile = self.font.get_small_font(ord(c))
            x_pos = x + n
            self.base_img.paste(tile, (x_pos * tile_step, y * self.tile_height,), )

    @staticmethod
    def fmt_float(txt: str) -> str:
        n = txt.find('.')
        d1 = txt[n-1:n]
        d2 = txt[n+1:n+2]
        ch1 = ord(d1) - 0x30
        ch2 = ord(d2) - 0x30
        ch1 += 0xA1
        ch2 += 0xB1

        result = [txt[:n-1], chr(ch1), chr(ch2), txt[n+2:]]

        return ''.join(result)

    def draw_srt(self, srt_frame: SrtFrame) -> None:
        x, y = self.cfg.srt_start_location
        if y < 0:   # location from screen bottom
            y += self.display_height

        for srt_item in self.cfg.srt_data:
            fmt_str = f'{srt_item.upper()}:{{}}'
            if srt_item in self.cfg.srt_fmt:
                fmt_str = self.cfg.srt_fmt[srt_item]
            data = getattr(srt_frame, srt_item)
            txt = fmt_str.format(data)
            if not self.cfg.ardu and '.' in txt:
                txt = self.fmt_float(txt)

            self.draw_str(x, y, txt)
            x += len(txt) + 1

    def char_reader(frame: Frame, x: int, y: int) -> str:
        pass

    def draw_frame(self, frame: Frame) -> None:

        if frame.size == 0:  # empty frame
            self.draw_str(0, 0, 'NO OSD DATA')
            return self.base_img

        gps_lat: tuple[int, int] | None = None
        gps_lon: tuple[int, int] | None = None
        alt: tuple[int, int] | None = None

        for y in range(self.internal_height):
            for x in range(self.internal_width):
                char = self.char_reader(frame, x, y)

                if self.cfg.hide_gps and char == self.exclusions.LAT_CHAR_CODE:
                    gps_lat = (x, y)
                    self._items_cache.gps_lat = (x, y)
                        
                if self.cfg.hide_gps and char == self.exclusions.LON_CHAR_CODE:
                    gps_lon = (x, y)
                    self._items_cache.gps_lon = (x, y)

                if self.cfg.hide_alt and char == self.exclusions.ALT_CHAR_CODE:
                    alt = (x, y)
                    self._items_cache.alt = (x, y)

                if self.cfg.hide_dist and char == self.exclusions.HOME_CHAR_CODE:
                    alt = (x, y)
                    self._items_cache.dist = (x, y)

                if char != self.char_reader(self.last_frame, x, y):
                    tile = self.font[char]
                    self.base_img.paste(tile, (x * self.tile_width, y * self.tile_height,), )

        # hide gps/alt data
        # if any of items was present on frame we will use cache to be sure that all are deleted
        if gps_lat or gps_lon or alt:
            self.hide_items()

        self.last_frame = frame

    def render_single_frame_in_memory(self, frames_idx_render) -> Image.Image:
        for idx in frames_idx_render:
            yield from self._render_single_frame_in_memory(idx)

    def _render_single_frame_in_memory(self, idx: tuple) -> Image.Image:
        frame_ranges, srt = idx
        osd_frame = self.frames[frame_ranges]
        frame_file_id = osd_frame.idx
        self.draw_frame(frame=osd_frame)

        if self.cfg.overlay_img:
            self.base_img.paste(self.cfg.overlay_img, self.cfg.overlay_location)

        if len(srt) == 0:
            frame_ranges = [(frame_file_id, osd_frame.next_idx, None, )]
        elif len(srt) == 1:
            frame_ranges = [(frame_file_id, osd_frame.next_idx, self.srt_frames[srt[0]], )]
        else:
            srt_data = None
            if srt[0]:
                srt_data = self.srt_frames[srt[0]]

            frame_ranges = [(frame_file_id, self.srt_frames[srt[1]].idx, srt_data, )]
            for i in range(1, len(srt) - 1):
                n1 = srt[i]
                n2 = srt[i+1]
                frame_ranges.append((self.srt_frames[n1].idx, self.srt_frames[n2].idx, self.srt_frames[n1],))
            frame_ranges.append((self.srt_frames[srt[-1]].idx, osd_frame.next_idx, self.srt_frames[srt[-1]]))

        for fr in frame_ranges:
            if fr[2]:
                self.draw_srt(fr[2])

            final_img = self.base_img.copy().resize(self.final_img_size, Image.Resampling.BILINEAR)
            membuf = BytesIO()
            final_img.save(membuf, format="png", compress_level=0)
            membuf.seek(0)
            img = membuf.read()

            yield img

            for _ in range(fr[0] + 1, fr[1]):
                yield img

    def render_test_frame(self, frame_idx: int, srt_frame_idx: int | None) -> Image.Image:
        # srt_frame: SrtFrame, idx: list[tuple]
        frame = self.frames[frame_idx]
        self.draw_frame(frame=frame)
        if self.cfg.overlay_img:
            self.base_img.paste(self.cfg.overlay_img, self.cfg.overlay_location)

        if srt_frame_idx and self.srt_frames:
            srt_frame = self.srt_frames[srt_frame_idx]
            self.draw_srt(srt_frame)

        osd_img = self.base_img.resize(self.final_img_size, Image.Resampling.LANCZOS)

        return osd_img


class DjiRenderer(BaseRenderer):
    def __init__(self, font: Font, cfg: Config, osd_type: int, frames: list[Frame], srt_frames: list[SrtFrame], reset_cache: bool = False) -> None:
        self.internal_width, self.internal_height = INTERNAL_W_H_DJI
        super().__init__(font, cfg, osd_type, frames, srt_frames, reset_cache)

    def char_reader(self, frame: Frame, x: int, y: int) -> str:
        return frame.data[y + x * self.internal_height]
    

class WsRenderer(BaseRenderer):
    def __init__(self, font: Font, cfg: Config, osd_type: int, frames: list[Frame], srt_frames: list[SrtFrame], reset_cache: bool = False) -> None:
        self.internal_width, self.internal_height = INTERNAL_W_H_WS
        super().__init__(font, cfg, osd_type, frames, srt_frames, reset_cache)

    def char_reader(self, frame: Frame, x: int, y: int) -> str:
        return frame.data[x + y * self.internal_width]


def get_renderer(osd_type: int):
    if osd_type == OSD_TYPE_DJI:
        return DjiRenderer

    return WsRenderer

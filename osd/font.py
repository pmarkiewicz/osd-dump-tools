from PIL import Image

from .const import HD_TILE_WIDTH, SD_TILE_WIDTH, HD_TILE_HEIGHT, SD_TILE_HEIGHT, TILES_PER_PAGE


class Font:
    def __init__(self, basename: str, is_hd: bool, small_font_scale: int):
        self.tile_width = SD_TILE_WIDTH
        self.tile_height = SD_TILE_HEIGHT

        if is_hd:
            self.tile_width = HD_TILE_WIDTH
            self.tile_height = HD_TILE_HEIGHT

        self.small_font_scale = small_font_scale
        self.small_font_cache = {}

        self.img = self._load_pair(basename)

    def _load_raw(self, path: str) -> Image.Image:
        with open(path, "rb") as f:
            data = f.read()
            img = Image.frombytes(
                "RGBA",
                (
                    self.tile_width,
                    self.tile_height * TILES_PER_PAGE,
                ),
                data,
            )

        return img

    def _load_pair(self, basename: str) -> Image.Image:
        font_1 = self._load_raw(f"{basename}.bin")
        font_2 = self._load_raw(f"{basename}_2.bin")

        font = Image.new("RGBA", (font_1.width, font_1.height + font_2.height))
        font.paste(font_1, (0, 0))
        font.paste(font_2, (0, font_1.height))

        return font

    def __getitem__(self, key: int) -> Image.Image:
        return self.img.crop(
            (
                0,
                key * self.tile_height,
                self.tile_width,
                key * self.tile_height + self.tile_height,
            )
        )

    def get_small_font(self, key: int) -> Image.Image:
        if key in self.small_font_cache:
            return self.small_font_cache[key]

        tile = self[key]
        tile_size = (int(self.tile_width * self.small_font_scale), int(self.tile_height * self.small_font_scale))

        small_tile = tile.resize(tile_size, Image.Resampling.LANCZOS)
        self.small_font_cache[key] = small_tile

        return small_tile

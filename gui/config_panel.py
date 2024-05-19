import flet as ft
import json

from .utils import cut_path
from .osd_state import OsdState, Events


class ConfigPanel(ft.Column):
    def __init__(
        self,
        page: ft.Page,
        osd_state: OsdState,
        events: Events,
        on_change,
        *args,
        **kwargs,
    ):
        self.osd_state = osd_state
        self.events = events
        self.page = page
        self.on_change = on_change

        self.hq_profile = ft.Checkbox(
            label="High quality profile for output (slower)",
            value=osd_state.hq,
            on_change=self.update_hq_profile,
        )

        self.use_h265 = ft.Checkbox(
            label="Use h265 (hevc) codec if possible",
            value=osd_state.use_h265,
            on_change=self.update_use_h265,
        )

        self.hide_gps = ft.Checkbox(
            label="GPS", value=osd_state.hide_gps, on_change=self.update_hide_gps
        )
        self.hide_alt = ft.Checkbox(
            label="Altitude", value=osd_state.hide_alt, on_change=self.update_hide_alt
        )
        self.hide_dist = ft.Checkbox(
            label="Distance", value=osd_state.hide_dist, on_change=self.update_hide_dist
        )
        self.max_alt_txt = ft.Text("Max alt:")
        self.max_alt = ft.Slider(
            min=0,
            max=250,
            value=osd_state.max_alt,
            divisions=25,
            label="{value}",
            expand=True,
            on_change_end=self.update_max_alt,
        )
        self._update_max_alt(osd_state.max_alt)

        srt_display = osd_state.srt_data

        self.srt_signal = ft.Checkbox(
            label="signal", value="signal" in srt_display, on_change=self.update_srt
        )
        self.srt_ch = ft.Checkbox(
            label="ch", value="ch" in srt_display, on_change=self.update_srt
        )
        self.srt_delay = ft.Checkbox(
            label="delay", value="delay" in srt_display, on_change=self.update_srt
        )
        self.srt_bitrate = ft.Checkbox(
            label="bitrate", value="bitrate" in srt_display, on_change=self.update_srt
        )

        self.out_bitrate_txt = ft.Text("Out bitrate:")
        self.out_bitrate = ft.Slider(
            min=25,
            max=100,
            value=osd_state.bitrate,
            divisions=15,
            label="{value}",
            expand=True,
            on_change_end=self.update_bitrate,
        )
        self._update_bitrate(osd_state.bitrate)

        self.font_folder = ft.TextField(
            hint_text="font folder...",
            expand=True,
            read_only=True,
            value=cut_path(osd_state.font_folder),
            text_size=12,
        )
        self.pick_font_file_dialog = ft.FilePicker(on_result=self.pick_out_font_result)

        self.output_resolution = ft.RadioGroup(
            value=osd_state.output_resolution.upper(),
            on_change=self.out_resultion_change,
            content=ft.Row(
                controls=[
                    ft.Radio(value="HD", label="HD (720)"),
                    ft.Radio(value="FHD", label="FHD (1080)"),
                    ft.Radio(value="2K", label="2k (1440)"),
                ],
            ),
        )

        super().__init__(*args, **kwargs)
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.wrap = False
        self.tight = True

        self.controls = [
            self.pick_font_file_dialog,
            ft.Row(
                spacing=10,
                controls=[
                    self.font_folder,
                    ft.IconButton(
                        icon=ft.icons.FILE_OPEN,
                        on_click=lambda _: self.pick_font_file_dialog.get_directory_path(),
                    ),
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self.out_bitrate_txt,
                    self.out_bitrate,
                ],
            ),
            ft.Row(
                spacing=10,
                wrap=True,
                controls=[
                    ft.Text("Out resolution"),
                    self.output_resolution,
                ],
            ),
            self.hq_profile,
            self.use_h265,
            ft.Row(
                spacing=10,
                controls=[
                    ft.Text("Hide"),
                    self.hide_gps,
                    self.hide_dist,
                    self.hide_alt,
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    self.max_alt_txt,
                    self.max_alt,
                ],
            ),
            ft.Row(
                spacing=10,
                controls=[
                    ft.Text("Srt display"),
                    self.srt_signal,
                    self.srt_ch,
                    self.srt_delay,
                    self.srt_bitrate,
                ],
            ),
        ]

    def update_bitrate(self, e: ft.ControlEvent):
        bitrate = int(float(e.data))
        self._update_bitrate(bitrate)
        self.osd_state.bitrate = bitrate
        self.out_bitrate_txt.update()

    def update_max_alt(self, e: ft.ControlEvent):
        max_alt = int(float(e.data))
        self._update_max_alt(max_alt)
        self.osd_state.max_alt = max_alt
        self.max_alt_txt.update()

    def _update_max_alt(self, value: int):
        self.max_alt_txt.value = f"Max visible alt {value}"

    def _update_bitrate(self, value: int):
        self.out_bitrate_txt.value = f"Output bitrate {value}"

    def pick_out_font_result(self, e: ft.FilePickerResultEvent):
        if not e.data:
            return

        d = json.loads(e.data)
        self.font_folder.value = cut_path(d["path"])
        self.osd_state.font_load(d["path"])

        self.on_change()
        self.update()

    def out_resultion_change(self, e: ft.ControlEvent):
        self.osd_state.output_resolution = e.data

    def update_hide_gps(self, e: ft.ControlEvent) -> None:
        self.osd_state.hide_gps = e.data == "true"

    def update_hide_dist(self, e: ft.ControlEvent) -> None:
        self.osd_state.hide_dist = e.data == "true"

    def update_hide_alt(self, e: ft.ControlEvent) -> None:
        self.osd_state.hide_alt = e.data == "true"

    def update_srt(self, e: ft.ControlEvent) -> None:
        srt_disp = []
        if self.srt_bitrate.value:
            srt_disp.append("bitrate")
        if self.srt_ch.value:
            srt_disp.append("ch")
        if self.srt_delay.value:
            srt_disp.append("delay")
        if self.srt_signal.value:
            srt_disp.append("signal")

        self.osd_state.srt_data = srt_disp

    def update_hq_profile(self, e: ft.ControlEvent) -> None:
        self.osd_state.hq = e.data == "true"

    def update_use_h265(self, e: ft.ControlEvent) -> None:
        self.osd_state.use_h265 = e.data == "true"

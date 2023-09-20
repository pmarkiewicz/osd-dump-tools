import flet as ft

from .osd_state import OsdState, Events


class InfoPanel(ft.Column):
    def __init__(self, page: ft.Page, osd_state: OsdState, events: Events, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events
        self.page = page

        self.video_info = ft.Text('No video information')
        self.osd_info = ft.Text('No osd information')
        self.srt_info = ft.Text('No srt information')
        self.font_info = ft.Text('No font information')

        page.pubsub.subscribe_topic("video loaded", self.on_video_file_loaded)
        page.pubsub.subscribe_topic("osd loaded", self.on_osd_file_loaded)
        page.pubsub.subscribe_topic("srt loaded", self.on_srt_file_loaded)
        page.pubsub.subscribe_topic("font", self.on_font_loaded)

        super().__init__(*args, **kwargs)
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.wrap = False
        self.tight = True


        self.controls = [
            self.video_info,
            self.osd_info,
            self.srt_info,
            self.font_info,
        ]

    def on_video_file_loaded(self, topic: str, msg: str):
        self.video_info.value = msg
        self.video_info.update()

    def on_osd_file_loaded(self, topic: str, msg: str):
        self.osd_info.value = msg
        self.osd_info.update()

    def on_srt_file_loaded(self, topic: str, msg: str):
        self.srt_info.value = msg
        self.srt_info.update()

    def on_font_loaded(self, topic: str, msg: str):
        self.font_info.value = msg
        self.font_info.update()


import flet as ft

from .osd_state import OsdState, Events
from osd.utils.codecs import find_codec


class InfoPanel(ft.Column):
    def __init__(self, page: ft.Page, osd_state: OsdState, events: Events, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events
        self.page = page

        self.codec_info = ft.Text('No codec information')
        self.video_info = ft.Text('No video information')
        self.osd_info = ft.Text('No osd information')
        self.srt_info = ft.Text('No srt information')
        self.font_info = ft.Text('No font information')
        self.render_info = ft.Text('No estimation')

        page.pubsub.subscribe_topic("video loaded", self.on_video_file_loaded)
        page.pubsub.subscribe_topic("osd loaded", self.on_osd_file_loaded)
        page.pubsub.subscribe_topic("srt loaded", self.on_srt_file_loaded)
        page.pubsub.subscribe_topic("font", self.on_font_loaded)

        codec = find_codec()
        if codec:
            self.codec_info.value = f'Codec: {codec}'

        super().__init__(*args, **kwargs)
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.wrap = False
        self.tight = True

        self.controls = [
            self.codec_info,
            self.video_info,
            self.osd_info,
            self.srt_info,
            self.font_info,
            self.render_info,
        ]

    # TODO: refactor nested if
    def on_video_file_loaded(self, topic: str, msg: str):
        self.video_info.value = msg
        estimation = self.osd_state.estimate_render_time()
        if estimation:
            if int(estimation / 60) > 0:
                estimation = int(estimation / 60)
                self.render_info.value = f'Est render time: {estimation} mins'
            else:
                self.render_info.value = f'Est render time: {estimation} secs'
        else:
            self.render_info.value = 'No estimation'

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

import flet as ft
from functools import partial

from .osd_state import OsdState, Events
from osd.utils.codecs import find_codec_bknd


class InfoPanel(ft.Column):
    def __init__(self, page: ft.Page, osd_state: OsdState, events: Events, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events
        self.page = page
        self.app = page

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
        page.pubsub.subscribe_topic("codec", self.on_codec)
        page.pubsub.subscribe_topic("use_265_changed", self.on_use_265_changed)
        page.pubsub.send_all_on_topic('use_265_changed', None)

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

    def on_use_265_changed(self, topic: str, _: str):
        codec_notification = partial(self.app.pubsub.send_all_on_topic, 'codec')
        find_codec_bknd(codec_notification, self.osd_state.cfg.use_h265)

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

    def on_codec(self, topic: str, msg: str):
        self.codec_info.value = msg
        self.codec_info.update()

import flet as ft

from .osd_state import OsdState, Events

from .files_panel import FilesPanel
from .info_panel import InfoPanel
from .config_panel import ConfigPanel


class DataPanel(ft.Column):
    def __init__(self, page: ft.Page, osd_state: OsdState, events: Events, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events

        super().__init__(*args, **kwargs)

        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START
        self.wrap = False
        self.expand = 1
        self.tight = True

        self.files_panel = FilesPanel(page, self.osd_state, self.events, self.on_change, visible=True)
        self.info_panel = InfoPanel(page, self.osd_state, self.events, visible=True)
        self.config_panel = ConfigPanel(page, self.osd_state, self.events, self.on_change, visible=False)

        self.render_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render', expand=1, disabled=True, on_click=self.events.render)
        self.render_test_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Test frame', expand=1, on_click=self.on_test, disabled=True)
        self.render_last_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Last frame', expand=1, on_click=self.on_last, disabled=True)

        self.navi = ft.Tabs(
            selected_index=0,
            on_change=self.on_tabs_changed,
            tabs=[
                ft.Tab(text="Files"), 
                ft.Tab(text="Configuration"), 
                ],
        )

        self.controls = [
            # border=ft.border.all(1, ft.colors.BLUE_GREY_200), 
            ft.Container(margin=0, padding=2, alignment=ft.alignment.top_left, content=self.navi,),
            ft.Container(margin=0, padding=2, alignment=ft.alignment.top_left, content=self.files_panel),
            ft.Container(margin=0, padding=0, alignment=ft.alignment.top_left, content=self.info_panel),
            ft.Container(margin=0, padding=0, alignment=ft.alignment.top_left, content=self.config_panel),
            ft.Container(margin=0, padding=0, alignment=ft.alignment.top_left, content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.render_btn,
                    self.render_test_btn,
                    self.render_last_btn,
                ]
            )),
        ]

    def on_test(self, _):
        self.events.render_test_frame()

    def on_last(self, _):
        self.events.render_last_frame()

    def on_change(self):
        self.render_btn.disabled = not self.osd_state.is_render_ready
        self.render_test_btn.disabled = not self.osd_state.is_render_ready
        self.render_last_btn.disabled = not self.osd_state.is_render_ready
        self.update()

    def on_tabs_changed(self, e: ft.ControlEvent):
        id = int(e.data)

        self.files_panel.visible = id == 0
        self.info_panel.visible = id == 0
        self.config_panel.visible = id == 1

        self.update()

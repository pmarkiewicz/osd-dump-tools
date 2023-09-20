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

        self.files_panel = FilesPanel(page, self.osd_state, self.events, self.on_change, visible=True)
        self.info_panel = InfoPanel(page, self.osd_state, self.events, visible=True)
        self.config_panel = ConfigPanel(page, self.osd_state, self.events, self.on_change, visible=False)

        self.render_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render', expand=1, disabled=True, on_click=self.events.render)
        self.render_test_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render test frame', expand=1, on_click=self.events.render_test_frame, disabled=True)

        self.navi = ft.Tabs(
            selected_index=0,
            on_change=self.on_tabs_changed,
            tabs=[
                ft.Tab(text="Files"), 
                ft.Tab(text="Configuration"), 
                ],
        )

        self.controls = [
            self.navi,
            self.files_panel,
            ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
            self.info_panel,
            self.config_panel,
            ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
            ft.Row(
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    self.render_btn,
                    self.render_test_btn,
                ]
            ),
        ]

    def on_change(self):
        self.render_btn.disabled = not self.osd_state.is_render_ready
        self.render_test_btn.disabled = not self.osd_state.is_render_ready
        self.update()

    def on_tabs_changed(self, e: ft.ControlEvent):
        id = int(e.data)

        self.files_panel.visible = id == 0
        self.info_panel.visible = id == 0
        self.config_panel.visible = id == 1

        self.update()

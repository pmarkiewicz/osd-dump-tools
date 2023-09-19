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
        self.wrap = False
        self.expand = 1

        self.files_panel = FilesPanel(page, self.osd_state, self.events, self.on_change)
        self.info_panel = InfoPanel(page, self.osd_state, self.events)
        self.config_panel = ConfigPanel(page, self.osd_state, self.events)

        self.render_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render', expand=1, disabled=True, on_click=self.events.render)
        self.render_test_btn = ft.FilledButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render test frame', expand=1, on_click=self.events.render_test_frame, disabled=True)

        self.controls = [
            self.files_panel,
            ft.Text('Source files', size=30, weight=ft.FontWeight.BOLD),
            ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
            ft.Text('Info', size=30, weight=ft.FontWeight.BOLD),
            self.info_panel,
            ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
            ft.Text('Configuration', size=30, weight=ft.FontWeight.BOLD,),
            self.config_panel,
            ft.Divider(height=15, thickness=3, color=ft.colors.GREEN_500),
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

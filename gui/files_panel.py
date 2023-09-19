import flet as ft

from .osd_state import OsdState, Events


class FilesPanel(ft.UserControl):
    def __init__(self, page: ft.Page, osd_state: OsdState, events: Events, on_change, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events
        self.page = page
        self.on_change = on_change

        super().__init__(*args, **kwargs)
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.wrap = False

        self.pick_video_file_dialog = ft.FilePicker(on_result=self.pick_video_file_result)
        self.pick_osd_file_dialog = ft.FilePicker(on_result=self.pick_osd_file_result)
        self.pick_srt_file_dialog = ft.FilePicker(on_result=self.pick_srt_file_result)
        self.pick_out_file_dialog = ft.FilePicker(on_result=self.pick_out_file_result)

        self.video_file = ft.TextField(hint_text='video file...', expand=True, read_only=True)
        self.osd_file = ft.TextField(hint_text='osd file...', expand=True, read_only=True)
        self.srt_file = ft.TextField(hint_text='srt file...', expand=True, read_only=True)
        self.out_file = ft.TextField(hint_text='output file...', expand=True, read_only=True)

    def build(self):
        return ft.Column(controls=[
            ft.Row(
                spacing=10, 
                controls=[
                    self.video_file,
                    ft.FloatingActionButton(
                        icon=ft.icons.FILE_OPEN,
                        on_click=lambda _: self.pick_video_file_dialog.pick_files(
                            allow_multiple=False, allowed_extensions=['mp4'], dialog_title='Open video file',
                        ),
                    ),

                ]
            ),
            ft.Row(
                controls=[
                    self.osd_file,
                    ft.FloatingActionButton(icon=ft.icons.FILE_OPEN,
                        on_click=lambda _: self.pick_osd_file_dialog.pick_files(
                            allow_multiple=False, allowed_extensions=['osd'], dialog_title='Open osd file',
                        )
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    self.srt_file,
                    ft.FloatingActionButton(icon=ft.icons.FILE_OPEN,
                        on_click=lambda _: self.pick_srt_file_dialog.pick_files(
                            allow_multiple=False, allowed_extensions=['srt'], dialog_title='Open srt file',
                        )
                    ),
                ]
            ),
            ft.Row(
                controls=[
                    self.out_file,
                    ft.FloatingActionButton(icon=ft.icons.FILE_OPEN,
                        on_click=lambda _: self.pick_out_file_dialog.save_file(
                            allowed_extensions=['mp4'], 
                        )
                    ),
                ]
            ),
            self.pick_video_file_dialog,
            self.pick_osd_file_dialog,
            self.pick_srt_file_dialog,
            self.pick_out_file_dialog,

        ])

    def pick_video_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path

        self.osd_state.video_load(fn)

        self.video_file.value = self.osd_state._video_path
        self.osd_file.value = self.osd_state._osd_path
        self.srt_file.value = self.osd_state._srt_path
        self.out_file.value = self.osd_state._out_path
        self.on_change()
        self.update()

    def pick_osd_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.osd_file.value = fn
        self.osd_state.osd_path = fn
        self.osd_state.update_osd_info()

        self.on_change()
        self.update()

    def pick_srt_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.srt_file.value = fn
        self.osd_state.srt_path = fn
        self.osd_state.update_srt_info()

        self.on_change()
        self.update()

    def pick_out_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.out_file.value = fn
        self.osd_state.out_path = fn
        self.osd_state.update_out_info()

        self.on_change()
        self.out_file.update()


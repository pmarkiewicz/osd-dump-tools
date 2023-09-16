import pathlib
import flet as ft
import base64

from osd.const import CONFIG_FILE_NAME, OSD_TYPE_DJI, FW_ARDU, FW_BETAFL
from osd.config import Config
from osd.dji import read_dji_osd_frames
from osd.ws import read_ws_osd_frames
from osd.render import get_renderer
from osd.utils.video_props import get_video_properties
from osd.utils.osd_props import detect_system, decode_system_str
from osd.utils.srt import read_srt_frames

class OsdApp(ft.UserControl):
    def __init__(self, cfg: Config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.cfg = cfg
        self.osd_type = None
        self.frames = None
        self.firmware = None
        self.video_props = None

        self.pick_video_file_dialog = ft.FilePicker(on_result=self.pick_video_file_result)
        self.pick_osd_file_dialog = ft.FilePicker(on_result=self.pick_osd_file_result)
        self.pick_srt_file_dialog = ft.FilePicker(on_result=self.pick_srt_file_result)
        self.pick_out_file_dialog = ft.FilePicker(on_result=self.pick_out_file_result)
        self.pick_font_file_dialog = ft.FilePicker(on_result=self.pick_out_font_result)

        self.video_file = ft.TextField(hint_text='video file...', expand=True, read_only=True)
        self.osd_file = ft.TextField(hint_text='osd file...', expand=True, read_only=True)
        self.srt_file = ft.TextField(hint_text='srt file...', expand=True, read_only=True)
        self.out_file = ft.TextField(hint_text='output file...', expand=True, read_only=True)
        self.font_folder = ft.TextField(hint_text='font folder...', expand=True, read_only=True)

        self.video_info = ft.Text('No video information')
        self.osd_info = ft.Text('No osd information')
        self.srt_info = ft.Text('No srt information')
        self.font_info = ft.Text('No font information')

        self.preview = ft.Image(
                            width=600, 
                            src=r"E:\FPV\Video\DJI\20230912\test_image.png",
                            fit=ft.ImageFit.FIT_WIDTH,
                        )

    def pick_video_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path

        video_path = pathlib.Path(fn)
        video_stem = video_path.stem
        osd_path = video_path.with_suffix('.osd')
        srt_path = video_path.with_suffix('.srt')
        out_path = video_path.with_name(video_stem + "_with_osd.mp4")

        self.video_file.value = video_path
        self.osd_file.value = osd_path if osd_path.exists() else''
        self.srt_file.value = srt_path if srt_path.exists() else''
        self.out_file.value = out_path

        self.update_video_info()
        if not self.osd_file.value:
            self.reset_osd_info()
        else:
            self.detect_system()
            self.read_osd_frames()
            self.update_osd_info()

        if not self.srt_file.value:
            self.reset_srt_info()
        else:
            self.read_srt_frames()
            self.update_srt_info()

        self.update()

    def update_video_info(self):
        self.video_props = get_video_properties(self.video_file.value)
        self.video_info.value = f'Source video: {self.video_props.width}x{self.video_props.height} {self.video_props.fps}fps'

    def detect_system(self):
        self.osd_type, self.firmware = detect_system(self.osd_file.value)

    def update_osd_info(self):
        osd_name = 'DJI' if self.osd_type == OSD_TYPE_DJI else 'WS'
        fw_name = decode_system_str(self.firmware)

        self.osd_info.value = f'System: {osd_name}, fw: {fw_name}, loaded {len(self.frames)} osd frames'

    def reset_osd_info(self):
        self.osd_info.value = 'No osd information'

    def read_osd_frames(self):
        if self.osd_type == OSD_TYPE_DJI:
            self.frames = read_dji_osd_frames(self.osd_file.value, False, self.cfg)
        else:
            self.frames = read_ws_osd_frames(self.osd_file.value, False, self.cfg)

    def update_srt_info(self):
        self.srt_info.value = f'Loaded {len(self.srt_frames)} srt frames'

    def reset_srt_info(self):
        self.osd_info.value = 'No srt information'

    def read_srt_frames(self):
        self.srt_frames = read_srt_frames(self.srt_file.value, False, self.video_props.fps)            

    def render_test_frame(self) -> None:
        cls = get_renderer(self.osd_type)
        renderer = cls(font=self.font, cfg=self.cfg, osd_type=self.osd_type, frames=self.frames, srt_frames=self.srt_frames)
        img = renderer.render_test_frame(50, 50)
        base64_bytes = base64.b64encode(img)
        self.preview.src_base64 = base64_bytes
        self.preview.update()


    def pick_osd_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.osd_file.value = fn

        self.osd_file.update()

    def pick_srt_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.srt_file.value = fn

        self.srt_file.update()

    def pick_out_file_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = e.files[0].path
        self.out_file.value = fn

        self.out_file.update()

    def pick_out_font_result(self, e: ft.FilePickerResultEvent):
        if not e.files:
            return
        
        fn = pathlib.Path(e.files[0].path)

        self.font_folder.value = fn.parent

        self.font_folder.update()

    def build(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_EVENLY,
            controls=[
                self.pick_video_file_dialog,
                self.pick_osd_file_dialog,
                self.pick_srt_file_dialog,
                self.pick_out_file_dialog,
                self.pick_font_file_dialog,
                ft.Column(
                    spacing=5,
                    alignment=ft.MainAxisAlignment.START,
                    wrap=False,
                    expand=1,
                    controls=[
                        ft.Text('Source files', size=30, weight=ft.FontWeight.BOLD),
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
                        ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
                        self.video_info,
                        self.osd_info,
                        self.srt_info,
                        self.font_info,
                        ft.Divider(height=9, thickness=3, color=ft.colors.GREEN_500),
                        ft.Text('Configuration', size=30, weight=ft.FontWeight.BOLD,),
                        ft.Row(
                            spacing=10, 
                            controls=[
                                self.font_folder,
                                ft.FloatingActionButton(icon=ft.icons.FILE_OPEN,
                                    on_click=lambda _: self.pick_font_file_dialog.pick_files(
                                        allow_multiple=False, allowed_extensions=['bin'], dialog_title='Open any font file',
                                    )
                                ),
                            ]
                        ),
                        ft.Row(
                            spacing=10, 
                            controls=[
                                ft.Text('Output bitrate'),
                                ft.Slider(min=25, max=100, value=50, divisions=15, label="{value}", expand=True)
                            ]
                        ),
                        ft.Row(
                            spacing=10, 
                            controls=[
                                ft.Text('Output resulution'),
                                ft.RadioGroup(
                                    value='HD',
                                    content=ft.Row(
                                        controls=[
                                            ft.Radio(value="HD", label="HD (720)"),
                                            ft.Radio(value="FHD", label="FHD (1080)"),
                                            ft.Radio(value="2k", label="2k (1440)")
                                        ],
                                    ),
                                ),
                            ]
                        ),
                        ft.Checkbox(label='High quality profile for output (slower)', value=False),
                        ft.Row(
                            spacing=10, 
                            controls=[
                                ft.Text('Hide'),
                                ft.Checkbox(label='GPS', value=True),
                                ft.Checkbox(label='Altitude', value=True),
                                ft.Checkbox(label='Distance', value=True),
                            ]

                        ),
                        ft.Row(
                            spacing=10, 
                            controls=[
                                ft.Text('Display'),
                                ft.Checkbox(label='signal', value=False),
                                ft.Checkbox(label='ch', value=False),
                                ft.Checkbox(label='delay', value=True),
                                ft.Checkbox(label='bitrate', value=True),
                            ]

                        ),
                        ft.Divider(height=15, thickness=3, color=ft.colors.GREEN_500),
                        ft.Row(
                            alignment=ft.MainAxisAlignment.CENTER,
                            controls=[
                                ft.FloatingActionButton(icon=ft.icons.FILE_OPEN_OUTLINED, text='Render', expand=True),
                            ]
                        ),
                    ]
                ),
                ft.Column(
                    expand=2,
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        self.preview,
                    ]
                ),
            ]
        )
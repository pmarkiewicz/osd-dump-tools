import flet as ft
import base64
from io import BytesIO
from PIL import Image

from .osd_state import OsdState, Events


class PreviewPanel(ft.Column):
    def __init__(self, osd_state: OsdState, events: Events, *args, **kwargs):
        self.osd_state = osd_state
        self.events = events

        super().__init__(*args, **kwargs)

        img = self._create_empty_img()
        empty_image = base64.b64encode(img).decode()
        self.preview = ft.Image(
                src_base64=empty_image,
                fit=ft.ImageFit.FIT_WIDTH,
                visible=False
            )

        self.no_preview = ft.Text('Preview not rendered')

        self.expand = 2
        self.spacing = 5
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER
        self.controls = [
            ft.Container(margin=0, padding=0, alignment=ft.alignment.center, bgcolor=ft.colors.BLUE_GREY_100, content=self.preview),
            ft.Container(margin=0, padding=0, alignment=ft.alignment.center, content=self.no_preview),
        ]

    def set_preview(self, img_base64):
        self.preview.src_base64 = img_base64
        self.preview.visible = True
        self.no_preview.visible = False
        self.update()

    def reset_preview(self, img_base64):
        self.preview.visible = False
        self.no_preview.visible = True
        self.update()

    def _create_empty_img(self):
        img = Image.new("RGB", (5, 5), color=(200, 0, 0,))
        membuf = BytesIO()
        img.save(membuf, format="png")
        membuf.seek(0)
        img = membuf.read()

        return img

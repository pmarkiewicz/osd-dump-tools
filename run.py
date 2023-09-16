import pathlib

import flet as ft

from gui.osd_app import OsdApp
from osd.config import ConfigParser, Config
from osd.const import CONFIG_FILE_NAME


def main(page: ft.Page):
    cfg = ConfigParser()
    cfg.read(pathlib.PurePath(__file__) / CONFIG_FILE_NAME)
    cfg.read(pathlib.Path.home() / CONFIG_FILE_NAME)

    args = Config(cfg)

    page.title = "OSD Overlay"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.update()

    # create application instance
    osd_app = OsdApp(cfg=args)

    # add application's root control to the page
    page.add(osd_app)

if __name__ == "__main__":
    ft.app(target=main)
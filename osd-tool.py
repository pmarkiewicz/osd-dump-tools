import pathlib
from configparser import ConfigParser

import flet as ft

from gui.osd_app import OsdApp
from osd.config import Config
from osd.const import CONFIG_FILE_NAME


def main(page: ft.Page):
    cfg = ConfigParser()
    cfg.read(pathlib.Path(__file__).resolve().parent / 'osd' / CONFIG_FILE_NAME)
    args = Config(cfg)

    local_cfg = ConfigParser()
    local_cfg.read(pathlib.Path.home() / CONFIG_FILE_NAME)
    args.update_cfg(local_cfg)
    args.calculate()

    page.title = "OSD Overlay"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment_alignment = ft.MainAxisAlignment.START
    page.spacing = 5
    page.padding = 5
    page.update()

    # create application instance
    osd_app = OsdApp(cfg=args, page=page)

    # add application's root control to the page
    page.add(osd_app)


if __name__ == "__main__":
    ft.app(target=main)

import flet as ft
from flet import AlertDialog
import base64
from io import BytesIO
import time
from threading import Thread
import re

from .preview_panel import PreviewPanel
from .data_panel import DataPanel
from .osd_state import OsdState, Events

from osd.config import Config
from osd.render import get_renderer
from osd.run_ffmpeg import run_ffmpeg_stdin
from osd.utils.find_slot import find_slots


def logger(process, page):
    regex = re.compile(r'frame=\s*(\d+)')
    s = ''
    while process.poll() is None:
        s += process.stderr.read(20).decode('ascii')
        if s.find('\r') != -1:
            str = s.split('\r')
            m = regex.search(str[0])
            if m:
                frame = int(m.group(1))
            page.pubsub.send_all_on_topic('render', (frame, str[0], ))
            if len(str) > 1:
                s = str[1]
            else:
                s = ''


class OsdApp(ft.UserControl):
    def __init__(self, page: ft.Page, cfg: Config, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.page = page
        self.osd_state = OsdState(page=page, cfg=cfg, )
        self.osd_state.error_handler = self.on_error
        self.osd_state.info_handler = self.on_info

        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.START

        # TODO: get form config
        self.events = Events(
            update=self.update, 
            render=self.render, 
            render_test_frame=self.render_test_frame,
            reset_preview=self.reset_preview,
            render_last_frame=self.render_last_frame
        )

        self.preview_panel = PreviewPanel(self.osd_state, self.events)
        self.data_panel = DataPanel(page, self.osd_state, self.events)

        self.err_dialog = AlertDialog(
                modal=True,
                title=ft.Text("Error"),
                content=ft.Text(""),
                actions=[
                    ft.TextButton("Close", on_click=self.close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

        self.info_dialog = AlertDialog(
                modal=True,
                title=ft.Text("Info"),
                content=ft.Text(""),
                actions=[
                    ft.TextButton("Close", on_click=self.close_dlg),
                ],
                actions_alignment=ft.MainAxisAlignment.END
            )

        self.render_dialog = RenderDialog(page)
        page.pubsub.subscribe_topic("error", self.on_error_msg)

    def on_error_msg(self, topic: str, msg: str):
        self.on_error(msg)

    def close_dlg(self, e):
        self.err_dialog.open = False
        self.info_dialog.open = False
        self.render_dialog.open = False
        self.page.update()

    def on_info(self, msg: str) -> None:
        self.info_dialog.content.value = str(msg)
        self.info_dialog.open = True
        self.page.dialog = self.info_dialog
        self.page.update()

    def on_error(self, msg: str) -> None:
        self.err_dialog.content.value = str(msg)
        self.err_dialog.open = True
        self.page.dialog = self.err_dialog
        self.page.update()

    def on_render(self):
        self.render_dialog.open = True
        self.render_dialog.total_frames = self.osd_state.video_props.frame_count
        self.page.dialog = self.render_dialog
        self.render_dialog.reset()
        self.page.update()

    def reset_preview(self):
        self.preview_panel.reset_preview()

    def render_last_frame(self, e: ft.ControlEvent = None) -> None:
        if not (self.osd_state.osd_type and self.osd_state.font and self.osd_state.frames):
            return

        self._render_test_frame(-1, -1)

    def render_test_frame(self, e: ft.ControlEvent = None) -> None:
        if not (self.osd_state.osd_type and self.osd_state.font and self.osd_state.frames):
            return

        self._render_test_frame(50, 50)

    def _render_test_frame(self, frame_idx: int, srt_frame_idx: int) -> None:
        cls = get_renderer(self.osd_state.osd_type)
        renderer = cls(font=self.osd_state.font, cfg=self.osd_state.cfg, osd_type=self.osd_state.osd_type, frames=self.osd_state.frames, srt_frames=self.osd_state.srt_frames, reset_cache=True)
        img = renderer.render_test_frame(frame_idx, srt_frame_idx)

        membuf = BytesIO()
        img.save(membuf, format="png")
        membuf.seek(0)
        img = membuf.read()

        base64_bytes = base64.b64encode(img)
        self.preview_panel.set_preview(base64_bytes.decode())

    def render(self, e: ft.ControlEvent):
        if not (self.osd_state.osd_type and self.osd_state.font and self.osd_state.frames):
            return

        self.on_render()

        cls = get_renderer(self.osd_state.osd_type)
        renderer = cls(font=self.osd_state.font, cfg=self.osd_state.cfg, osd_type=self.osd_state.osd_type, frames=self.osd_state.frames, srt_frames=self.osd_state.srt_frames, reset_cache=True)

        render_time_start = time.time()
        frames_idx_render = []
        if self.osd_state.srt_frames:
            srt_idxs = [srt.idx for srt in self.osd_state.srt_frames]

            for idx, frame in enumerate(self.osd_state.frames[:-1]):
                start_frame = frame.idx
                next_frame = frame.next_idx
                slot_frames = find_slots(srt_idxs, start_frame, next_frame)
                frames_idx_render.append((idx, slot_frames,))
        else:
            frames_idx_render = [(idx, None,) for idx, _ in enumerate(self.osd_state.frames[:-1])]

        try:
            process = run_ffmpeg_stdin(self.osd_state.cfg, self.osd_state.video_path, self.osd_state.out_path)
        except OSError:
            self.close_dlg(None)
            self.on_error('Cannot start ffmpeg')
            return

        self.render_dialog.process = process

        th = Thread(target=logger, args=(process, self.page, ))
        th.start()
        time.sleep(0)

        for img in renderer.render_single_frame_in_memory(frames_idx_render):
            time.sleep(0)
            try:
                process.stdin.write(img)
            except BrokenPipeError:
                # process was terminated
                break
            except OSError:
                break

        # Close the pipe to signal the end of input
        process.stdin.close()

        # Wait for ffmpeg to finish
        process.wait()

        self.close_dlg(None)
        time.sleep(0)
        # self.on_info('Rendering complete')

        render_time = time.time() - render_time_start
        self.osd_state.render_time(render_time)

    def build(self):
        return ft.Row(
            alignment=ft.MainAxisAlignment.START,
            controls=[
                self.data_panel,
                ft.VerticalDivider(width=50, thickness=3, color=ft.colors.GREEN_500),
                self.preview_panel,
                ]
        )

    def update(self):
        return super().update()


class RenderDialog(AlertDialog):
    def __init__(self, page: ft.Page, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.total_frames = 0
        self.process = None

        page.pubsub.subscribe_topic("render", self.on_render_update)

        self.modal = True
        self.title = ft.Text("Render in progress")
        self.actions_alignment = ft.MainAxisAlignment.END

        self.actions = [
            ft.TextButton("Abort", on_click=self.abort),
        ]

        self.progress = ft.ProgressBar(width=900, color="amber", bgcolor="#eeeeee", value=0.0)
        self.console = ft.Text("....", color=ft.colors.WHITE, bgcolor=ft.colors.BLACK, width=900, size=12)
        self.content = ft.Column(alignment=ft.MainAxisAlignment.START,
                                 controls=[
                                    self.progress,
                                    self.console,
                                  ],
                                )

    def on_render_update(self, topic: str, args):
        frame, msg = args

        self.console.value = msg
        self.progress.value = frame / self.total_frames
        self.update()

    def reset(self):
        self.console.value = '...'
        self.progress.value = 0.0

    def abort(self, e: ft.ControlEvent):
        if self.process:
            self.process.terminate()

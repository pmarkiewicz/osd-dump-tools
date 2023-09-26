from dataclasses import dataclass
import pathlib

import cv2


@dataclass(slots=True)
class VideoProperties:
    fps: int
    width: int
    height: int
    frame_count: int
    duration_min: int
    duration_sec: int


def get_video_properties(mp4_filename: pathlib.Path) -> VideoProperties:
    mp4_filename = str(mp4_filename)
    try:
        vcap = cv2.VideoCapture(mp4_filename)
        fps = int(vcap.get(cv2.CAP_PROP_FPS))
        width  = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        frame_count = int(vcap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = int(frame_count/fps)
        duration_min = int(duration / 60)
        duration_sec = duration % 60
        return VideoProperties(fps, width, height, frame_count, duration_min, duration_sec)
    
    except Exception as e:
        print(f"Cannot read fps from {mp4_filename}, {e}")
        return None
    finally:
        vcap.release()
         

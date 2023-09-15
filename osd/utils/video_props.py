from dataclasses import dataclass
import pathlib

import cv2


@dataclass(slots=True)
class VideoProperties:
    fps: int
    width: int
    height: int


def get_video_properties(mp4_filename: pathlib.Path) -> VideoProperties:
    mp4_filename = str(mp4_filename)
    try:
        vcap = cv2.VideoCapture(mp4_filename)
        fps = int(vcap.get(cv2.CAP_PROP_FPS))
        width  = int(vcap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(vcap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        return VideoProperties(fps, width, height)
    
    except Exception as e:
        print(f"Cannot read fps from {mp4_filename}, {e}")
        return None
    finally:
        vcap.release()
         

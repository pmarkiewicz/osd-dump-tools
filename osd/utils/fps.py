import cv2


def get_fps(mp4_filename):
    mp4_filename = str(mp4_filename)
    try:
        cap = cv2.VideoCapture(mp4_filename)
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        return fps
    except Exception as e:
        print(f"Cannot read fps from {mp4_filename}, {e}")
        return None
    finally:
        cap.release()
         

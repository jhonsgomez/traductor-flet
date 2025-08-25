import cv2
import base64


def bgr_frame_to_base64(frame, quality: int = 80) -> str:
    """Convierte un frame BGR de OpenCV a base64 (JPEG)."""
    ok, buf = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    if not ok:
        return ""
    return base64.b64encode(buf).decode("utf-8")

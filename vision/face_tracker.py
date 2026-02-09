# vision/face_tracker.py
import os
import cv2 as cv
import config


class FaceTracker:
    def __init__(self):
        self.deadband_px = config.DEADBAND_PX

        # Downscale factor for detection speed
        self.detect_scale = float(getattr(config, "FACE_DETECT_SCALE", 0.5))

        # Smoothing factor for face center stability
        self.alpha = float(getattr(config, "FACE_CENTER_ALPHA", 0.25))
        self._smoothed_center = None

        # ----------------------------
        # Cascade path (NO cv.data usage)
        # ----------------------------
        cascade_path = getattr(config, "FACE_CASCADE_PATH", None)

        if cascade_path and os.path.exists(cascade_path):
            chosen = cascade_path
        else:
            candidates = [
                "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
                "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml",
                os.path.join(os.getcwd(), "haarcascade_frontalface_default.xml"),
            ]
            chosen = None
            for p in candidates:
                if os.path.exists(p):
                    chosen = p
                    break

            if chosen is None:
                raise RuntimeError(
                    "Could not find Haar cascade file.\n"
                    "Tried:\n"
                    " - config.FACE_CASCADE_PATH (but it was missing/invalid)\n"
                    " - /usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml\n"
                    " - /usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml\n"
                    " - ./haarcascade_frontalface_default.xml\n\n"
                    "Fix options:\n"
                    "1) Install OpenCV haarcascades package (opencv-data) OR\n"
                    "2) Put the xml in your project folder OR\n"
                    "3) Set FACE_CASCADE_PATH in config.py to the correct file path."
                )

        self.face_cascade = cv.CascadeClassifier(chosen)
        if self.face_cascade.empty():
            raise RuntimeError(
                f"Failed to load Haar face cascade.\n"
                f"Tried path: {chosen}\n"
                f"File exists but OpenCV couldn't load it (corrupt file or incompatible build)."
            )

        print(f"[INFO] Face cascade loaded: {chosen}")

    def _smooth_center(self, cx: int, cy: int):
        if self._smoothed_center is None:
            sx, sy = float(cx), float(cy)
        else:
            sx, sy = self._smoothed_center
            sx = (1 - self.alpha) * sx + self.alpha * cx
            sy = (1 - self.alpha) * sy + self.alpha * cy
        self._smoothed_center = (sx, sy)
        return int(sx), int(sy)

    def process(self, frame_bgr):
        H, W = frame_bgr.shape[:2]

        gray = cv.cvtColor(frame_bgr, cv.COLOR_BGR2GRAY)

        result = {
            "found": False,
            "bbox": None,
            "center": None,
            "raw_center": None,
            "error": None,
            "area": 0,
            "mask": None,
        }

        # Downscale for faster detection
        s = self.detect_scale
        if 0 < s < 1.0:
            small = cv.resize(gray, (0, 0), fx=s, fy=s)
        else:
            small = gray
            s = 1.0

        faces = self.face_cascade.detectMultiScale(
            small,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
        )

        if len(faces) == 0:
            self._smoothed_center = None
            return result

        # Largest face in small coords
        x, y, w, h = max(faces, key=lambda r: r[2] * r[3])

        # Scale back to full frame coords
        x = int(x / s)
        y = int(y / s)
        w = int(w / s)
        h = int(h / s)

        raw_cx = x + w // 2
        raw_cy = y + h // 2

        cx, cy = self._smooth_center(raw_cx, raw_cy)

        error_x = cx - (W // 2)
        error_y = cy - (H // 2)

        if abs(error_x) < self.deadband_px:
            error_x = 0
        if abs(error_y) < self.deadband_px:
            error_y = 0

        result.update({
            "found": True,
            "bbox": (int(x), int(y), int(w), int(h)),
            "center": (int(cx), int(cy)),
            "raw_center": (int(raw_cx), int(raw_cy)),
            "error": (int(error_x), int(error_y)),
            "area": int(w * h),
        })
        return result

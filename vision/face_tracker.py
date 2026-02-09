# vision/face_tracker.py
import os
import cv2 as cv
import config


def _first_existing(paths):
    for p in paths:
        if p and os.path.exists(p):
            return p
    return None


class FaceTracker:
    def __init__(self):
        self.deadband_px = config.DEADBAND_PX
        self.detect_scale = float(getattr(config, "FACE_DETECT_SCALE", 0.5))
        self.alpha = float(getattr(config, "FACE_CENTER_ALPHA", 0.25))
        self._smoothed_center = None

        # --- Resolve cascade paths (no cv.data usage) ---
        frontal_cfg = getattr(config, "FACE_CASCADE_FRONTAL", None)
        profile_cfg = getattr(config, "FACE_CASCADE_PROFILE", None)

        frontal_path = _first_existing([
            frontal_cfg,
            "/usr/share/opencv4/haarcascades/haarcascade_frontalface_default.xml",
            "/usr/share/opencv/haarcascades/haarcascade_frontalface_default.xml",
            os.path.join(os.getcwd(), "haarcascade_frontalface_default.xml"),
        ])

        profile_path = _first_existing([
            profile_cfg,
            "/usr/share/opencv4/haarcascades/haarcascade_profileface.xml",
            "/usr/share/opencv/haarcascades/haarcascade_profileface.xml",
            os.path.join(os.getcwd(), "haarcascade_profileface.xml"),
        ])

        if frontal_path is None:
            raise RuntimeError("Missing frontal cascade xml. Install opencv-data or set FACE_CASCADE_FRONTAL.")
        if profile_path is None:
            raise RuntimeError("Missing profile cascade xml. Install opencv-data or set FACE_CASCADE_PROFILE.")

        self.frontal = cv.CascadeClassifier(frontal_path)
        self.profile = cv.CascadeClassifier(profile_path)

        if self.frontal.empty():
            raise RuntimeError(f"Failed to load frontal cascade: {frontal_path}")
        if self.profile.empty():
            raise RuntimeError(f"Failed to load profile cascade: {profile_path}")

        print(f"[INFO] Frontal cascade: {frontal_path}")
        print(f"[INFO] Profile cascade: {profile_path}")

    def _smooth_center(self, cx: int, cy: int):
        if self._smoothed_center is None:
            sx, sy = float(cx), float(cy)
        else:
            sx, sy = self._smoothed_center
            sx = (1 - self.alpha) * sx + self.alpha * cx
            sy = (1 - self.alpha) * sy + self.alpha * cy
        self._smoothed_center = (sx, sy)
        return int(sx), int(sy)

    def _detect(self, small_gray):
        """
        Returns list of (x,y,w,h) in small image coords from:
        - frontal
        - profile
        - mirrored profile (to catch both left and right profiles)
        """
        detections = []

        # Frontal
        faces_f = self.frontal.detectMultiScale(
            small_gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30)
        )
        for (x, y, w, h) in faces_f:
            detections.append((x, y, w, h))

        # Profile (one direction)
        faces_p = self.profile.detectMultiScale(
            small_gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
        )
        for (x, y, w, h) in faces_p:
            detections.append((x, y, w, h))

        # Mirrored profile (other direction)
        flipped = cv.flip(small_gray, 1)
        faces_pf = self.profile.detectMultiScale(
            flipped, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30)
        )
        W = small_gray.shape[1]
        for (x, y, w, h) in faces_pf:
            # map flipped coords back to original
            x_unflip = W - (x + w)
            detections.append((x_unflip, y, w, h))

        return detections

    def process(self, frame_bgr):
        H, W = frame_bgr.shape[:2]
        gray = cv.cvtColor(frame_bgr, cv.COLOR_BGR2GRAY)

        # Improve robustness to lighting + profiles
        clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray = clahe.apply(gray)
        gray = cv.GaussianBlur(gray, (3, 3), 0)


        result = {
            "found": False,
            "bbox": None,
            "center": None,
            "raw_center": None,
            "error": None,
            "area": 0,
            "mask": None,
        }

        # Downscale for speed
        s = self.detect_scale
        if 0 < s < 1.0:
            small = cv.resize(gray, (0, 0), fx=s, fy=s)
        else:
            small = gray
            s = 1.0

        detections = self._detect(small)

        if not detections:
            self._smoothed_center = None
            return result

        # Choose largest detection
        x, y, w, h = max(detections, key=lambda r: r[2] * r[3])

        # Scale back to full-res coords
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

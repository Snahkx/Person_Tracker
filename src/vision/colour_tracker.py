# vision/colour_tracker.py
import cv2 as cv
import numpy as np
import config

class ColourTracker:
    def __init__(self, active_colors=None):
        self.active_colors = active_colors or config.ACTIVE_COLORS
        self.color_ranges = config.COLOR_RANGES
        self.min_area = config.MIN_AREA

        self.deadband_px = config.DEADBAND_PX
        self.alpha = config.CENTER_SMOOTH_ALPHA
        self.error_alpha = config.ERROR_SMOOTH_ALPHA

        self._smoothed_center = None
        self._smoothed_error = None

        self.kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, config.MASK_KERNEL)

    def _build_mask(self, hsv):
        mask = np.zeros(hsv.shape[:2], dtype=np.uint8)
        for color_name in self.active_colors:
            for lower, upper in self.color_ranges.get(color_name, []):
                mask = cv.bitwise_or(mask, cv.inRange(hsv, lower, upper))
        return mask

    def _smooth_center(self, cx, cy):
        if self._smoothed_center is None:
            self._smoothed_center = (float(cx), float(cy))
        else:
            sx, sy = self._smoothed_center
            sx = (1 - self.alpha) * sx + self.alpha * cx
            sy = (1 - self.alpha) * sy + self.alpha * cy
            self._smoothed_center = (sx, sy)
        return int(self._smoothed_center[0]), int(self._smoothed_center[1])

    def _smooth_error(self, ex, ey):
        if self._smoothed_error is None:
            self._smoothed_error = (float(ex), float(ey))
        else:
            sx, sy = self._smoothed_error
            sx = (1 - self.error_alpha) * sx + self.error_alpha * ex
            sy = (1 - self.error_alpha) * sy + self.error_alpha * ey
            self._smoothed_error = (sx, sy)
        return int(self._smoothed_error[0]), int(self._smoothed_error[1])

    def process(self, frame_bgr):
        H, W = frame_bgr.shape[:2]

        frame_bgr = cv.GaussianBlur(frame_bgr, (5, 5), 0)
        hsv = cv.cvtColor(frame_bgr, cv.COLOR_BGR2HSV)

        mask = self._build_mask(hsv)
        mask = cv.morphologyEx(mask, cv.MORPH_OPEN, self.kernel, iterations=config.OPEN_ITERS)
        mask = cv.morphologyEx(mask, cv.MORPH_CLOSE, self.kernel, iterations=config.CLOSE_ITERS)

        contours, _ = cv.findContours(mask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)

        result = {
            "found": False,
            "bbox": None,
            "center": None,
            "raw_center": None,
            "error": None,
            "area": 0,
            "mask": mask,
        }

        if not contours:
            self._smoothed_center = None
            self._smoothed_error = None
            return result

        c = max(contours, key=cv.contourArea)
        area = cv.contourArea(c)
        if area < self.min_area:
            self._smoothed_center = None
            self._smoothed_error = None
            return result

        x, y, w, h = cv.boundingRect(c)
        raw_cx = x + w // 2
        raw_cy = y + h // 2

        cx, cy = self._smooth_center(raw_cx, raw_cy)

        error_x = cx - (W // 2)
        error_y = cy - (H // 2)
        error_x, error_y = self._smooth_error(error_x, error_y)

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
            "area": int(area),
        })
        return result

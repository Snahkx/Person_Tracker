# vision/person_tracker.py
import cv2 as cv
import config

class PersonTracker:
    def __init__(self):
        self.deadband_px = config.DEADBAND_PX
        self.hog = cv.HOGDescriptor()
        self.hog.setSVMDetector(cv.HOGDescriptor_getDefaultPeopleDetector())

    def process(self, frame_bgr):
        H, W = frame_bgr.shape[:2]

        rects, weights = self.hog.detectMultiScale(
            frame_bgr, winStride=(8, 8), padding=(8, 8), scale=1.05
        )

        # no real mask here; keep None or a blank mask if you prefer
        mask = None

        result = {
            "found": False,
            "bbox": None,
            "center": None,
            "raw_center": None,
            "error": None,
            "area": 0,
            "mask": mask,
        }

        if len(rects) == 0:
            return result

        # choose largest
        x, y, w, h = max(rects, key=lambda r: r[2] * r[3])
        cx = x + w // 2
        cy = y + h // 2

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
            "raw_center": (int(cx), int(cy)),
            "error": (int(error_x), int(error_y)),
            "area": int(w * h),
        })
        return result

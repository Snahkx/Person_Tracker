"""
Docstring for distance.estimator
estimates the distance away from the camera
"""

import config

class DistanceEstimator:
    """
    Monocular distance using pinhole model:
        distance_cm = (known_width_cm * focal_px) / bbox_width_px

    focal_px is calibrated once from a known distance:
        focal_px = (bbox_width_px * calib_distance_cm) / known_width_cm
    """

    def __init__(self):
        self.known_width_cm = float(getattr(config, "KNOWN_TARGET_WIDTH_CM", 16.0))
        self.calib_distance_cm = float(getattr(config, "CALIB_DISTANCE_CM", 50.0))
        self.focal_px = getattr(config, "FOCAL_LENGTH_PX", None)

        self.alpha = float(getattr(config, "DIST_SMOOTH_ALPHA", 0.25))
        self._smoothed = None

    def calibrate(self, bbox_width_px: int):
        if bbox_width_px <= 0:
            return None
        self.focal_px = (float(bbox_width_px) * self.calib_distance_cm) / self.known_width_cm
        self._smoothed = None
        return self.focal_px

    def estimate_cm(self, bbox_width_px: int):
        if self.focal_px is None or bbox_width_px <= 0:
            return None

        dist = (self.known_width_cm * float(self.focal_px)) / float(bbox_width_px)

        if self._smoothed is None:
            self._smoothed = dist
        else:
            self._smoothed = (1 - self.alpha) * self._smoothed + self.alpha * dist

        return self._smoothed

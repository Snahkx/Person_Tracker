# main.py
import cv2 as cv
import config

from distance.estimator import DistanceEstimator
from vision.camera import Camera
from ui.overlay import draw_crosshair, draw_tracking_overlay
from vision.tracker import make_tracker

PanTiltController = None
if config.USE_SERVO:
    try:
        from servo.controller import PanTiltController
    except Exception:
        PanTiltController = None


def main():
    camera = Camera()
    dist_est = DistanceEstimator()

    # Tracker (we'll force colour inside vision/tracker.py if you changed it,
    # otherwise set TRACK_MODE="colour" in config.py)
    tracker = make_tracker(config.TRACK_MODE)

    controller = None
    if config.USE_SERVO and PanTiltController is not None:
        try:
            controller = PanTiltController()
        except Exception:
            controller = None

    try:
        while True:
            frame = camera.read()
            result = tracker.process(frame)  # dict

            # Distance from bbox width
            result["distance_cm"] = None
            bbox = result.get("bbox")
            if result.get("found") and isinstance(bbox, (tuple, list)) and len(bbox) == 4:
                w = int(bbox[2])
                result["distance_cm"] = dist_est.estimate_cm(w)

            # Servo control
            if controller is not None and result.get("found") and result.get("error"):
                error_x, error_y = result["error"]
                controller.update(error_x, error_y)

            # Overlays
            draw_crosshair(frame)
            draw_tracking_overlay(frame, result)

            # Display
            cv.imshow("Video", frame)
            mask = result.get("mask")
            if mask is not None:
                cv.imshow("Mask", mask)

            # --- Keys (ONLY calibration + quit) ---
            key = cv.waitKey(1) & 0xFF

            # Calibrate focal length using current bbox width
            if key == ord("c"):
                bbox = result.get("bbox")
                if result.get("found") and isinstance(bbox, (tuple, list)) and len(bbox) == 4:
                    w = int(bbox[2])
                    fp = dist_est.calibrate(w)
                    if fp is not None:
                        print(f"[CALIB] focal_px set to {fp:.2f}")

            # Quit
            elif key == ord("q"):
                break

    finally:
        camera.close()
        if controller is not None:
            controller.close()
        cv.destroyAllWindows()


#Checks if main is ran
if __name__ == "__main__":   
    main()

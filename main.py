# main.py
import cv2 as cv
import config

from distance.estimator import DistanceEstimator
from vision.camera import Camera
from ui.overlay import draw_crosshair, draw_tracking_overlay
from vision.tracker import make_tracker

# -----------------------------
# Servo import (safe / optional)
# -----------------------------
PanTiltController = None
if config.USE_SERVO:
    try:
        from servo.controller import PanTiltController
    except Exception:
        PanTiltController = None

# -----------------------------
# Mouse calibration flag
# -----------------------------
calibrate_requested = False


def on_mouse(event, x, y, flags, param):
    """
    Left click anywhere in the Video window to calibrate distance
    using the CURRENT bbox width.
    """
    global calibrate_requested
    if event == cv.EVENT_LBUTTONDOWN:
        calibrate_requested = True


def main():
    global calibrate_requested

    camera = Camera()
    dist_est = DistanceEstimator()

    tracker = make_tracker(config.TRACK_MODE)

    controller = None
    if config.USE_SERVO and PanTiltController is not None:
        try:
            controller = PanTiltController()
        except Exception:
            controller = None

    cv.namedWindow("Video")
    cv.setMouseCallback("Video", on_mouse)

    try:
        while True:
            frame = camera.read()
            result = tracker.process(frame)

            # -----------------------------
            # Distance estimation
            # -----------------------------
            result["distance_cm"] = None
            bbox = result.get("bbox")

            if result.get("found") and isinstance(bbox, (tuple, list)) and len(bbox) == 4:
                w = int(bbox[2])

                if calibrate_requested:
                    fp = dist_est.calibrate(w)
                    if fp is not None:
                        print(f"[CALIB] focal_px set to {fp:.2f}")
                    calibrate_requested = False

                result["distance_cm"] = dist_est.estimate_cm(w)

            # -----------------------------
            # Servo control
            # -----------------------------
            if controller is not None and result.get("found") and result.get("error"):
                error_x, error_y = result["error"]
                controller.update(error_x, error_y)

            # -----------------------------
            # Overlays + display
            # -----------------------------
            draw_crosshair(frame)
            draw_tracking_overlay(frame, result)

            cv.imshow("Video", frame)

            mask = result.get("mask")
            if mask is not None:
                cv.imshow("Mask", mask)

            if cv.waitKey(1) == 27:  # ESC quits
                break

    except KeyboardInterrupt:
        print("\n[INFO] Ctrl+C pressed, exiting...")

    finally:
        camera.close()
        if controller is not None:
            controller.close()
        cv.destroyAllWindows()


if __name__ == "__main__":
    main()

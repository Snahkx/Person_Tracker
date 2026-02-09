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

    # Tracker selected by config (face for your main goal)
    tracker = make_tracker(config.TRACK_MODE)

    # Servo controller (optional)
    controller = None
    if config.USE_SERVO and PanTiltController is not None:
        try:
            controller = PanTiltController()
        except Exception:
            controller = None

    # Window + mouse callback
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

                # Click-to-calibrate focal length
                if calibrate_requested:
                    fp = dist_est.calibrate(w)
                    if fp is not None:
                        print(f"[CALIB] focal_px set to {fp:.2f}")
                    calibrate_requested = False

                # Distance (only works after calibration OR if config.FOCAL_LENGTH_PX is set)
                result["distance_cm"] = dist_est.estimate_cm(w)

            # -----------------------------
            # Servo control
            # -----------------------------
            if controller is not None and result.get("found") and result.get("error"):
                error_x, error_y = result["error"]
                controller.update(error_x, error_y)

            # -----------------------------
            # Overlays
            # -----------------------------
            draw_crosshair(frame)
            draw_tracking_overlay(frame, result)

            # -----------------------------
            # Display
            # -----------------------------
            cv.imshow("Video", frame)

            # Face/person trackers don't generate masks; colour tracker does.
            mask = result.get("mask")
            if mask is not None:
                cv.imshow("Mask", mask)

            # Keep UI responsive (mouse events need waitKey)
            if cv.waitKey(1) == 27:  # ESC to quit
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

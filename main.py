# main.py
import time
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

    # OpenCV window + mouse callback
    cv.namedWindow("Video")
    cv.setMouseCallback("Video", on_mouse)

    # FPS tracking
    prev_time = time.time()
    fps = 0.0
    fps_smooth = 0.0
    fps_alpha = 0.15  # lower = smoother display

    # Distance throttling (huge FPS win on Pi)
    last_dist_t = 0.0
    DIST_UPDATE_S = 0.10  # 10 Hz distance updates

    try:
        while True:
            # ---- Capture + track ----
            frame = camera.read()
            result = tracker.process(frame)

            # ---- FPS timing (frame-to-frame) ----
            now = time.time()
            dt = now - prev_time
            prev_time = now
            if dt > 0:
                fps = 1.0 / dt
                fps_smooth = (
                    (1 - fps_alpha) * fps_smooth + fps_alpha * fps
                    if fps_smooth > 0
                    else fps
                )

            # ---- Distance estimation (throttled) ----
            bbox = result.get("bbox")
            if "distance_cm" not in result:
                result["distance_cm"] = None

            if result.get("found") and isinstance(bbox, (tuple, list)) and len(bbox) == 4:
                w = int(bbox[2])

                # Click-to-calibrate focal length
                if calibrate_requested:
                    fp = dist_est.calibrate(w)
                    if fp is not None:
                        print(f"[CALIB] focal_px set to {fp:.2f}")
                    calibrate_requested = False

                # Update distance only every DIST_UPDATE_S seconds (saves FPS)
                if dist_est.focal_px is not None and (now - last_dist_t) >= DIST_UPDATE_S:
                    result["distance_cm"] = dist_est.estimate_cm(w)
                    last_dist_t = now
            else:
                result["distance_cm"] = None

            # ---- Servo control ----
            if controller is not None and result.get("found") and result.get("error"):
                error_x, error_y = result["error"]
                controller.update(error_x, error_y)

            # ---- Overlays ----
            draw_crosshair(frame)
            draw_tracking_overlay(frame, result)

            # FPS overlay (top-left)
            cv.putText(
                frame,
                f"FPS: {fps_smooth:.1f}",
                (10, 30),
                cv.FONT_HERSHEY_SIMPLEX,
                0.8,
                (0, 255, 0),
                2,
            )

            # Calibration hint (only when not calibrated)
            if dist_est.focal_px is None:
                cv.putText(
                    frame,
                    "Left-click to CALIBRATE distance",
                    (10, 60),
                    cv.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 255, 0),
                    2,
                )

            # ---- Display ----
            cv.imshow("Video", frame)

            # IMPORTANT: showing Mask window costs FPS.
            # Only show it for colour mode.
            if config.TRACK_MODE == "colour":
                mask = result.get("mask")
                if mask is not None:
                    cv.imshow("Mask", mask)

            # Keep UI responsive (mouse events need waitKey)
            key = cv.waitKey(1) & 0xFF
            if key == 27:  # ESC quits
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

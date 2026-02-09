# config.py
import numpy as np

# ----------------------------
# Camera
# ----------------------------
PREVIEW_SIZE = (800, 600)  # default; override in config_local.py if you want

# ----------------------------
# Colour tracking (kept for later)
# ----------------------------
COLOR_RANGES = {
    "cb132b_red": [
        (
            np.array([0, 120, 60], dtype=np.uint8),
            np.array([10, 255, 255], dtype=np.uint8),
        ),
        (
            np.array([170, 120, 60], dtype=np.uint8),
            np.array([179, 255, 255], dtype=np.uint8),
        ),
    ],
}
ACTIVE_COLORS = ["cb132b_red"]

# ----------------------------
# Detection tuning (shared)
# ----------------------------
MIN_AREA = 1000
DEADBAND_PX = 12  # servo jitter killer (try 10–20)

# ----------------------------
# Mode
# ----------------------------
USE_SERVO = True
TRACK_MODE = "face"  # "person" | "colour" | "face"

# ----------------------------
# Servo pins
# ----------------------------
PAN_PIN = 18
TILT_PIN = 13

# ----------------------------
# pigpio servo settings (µs)
# ----------------------------
PAN_US_MIN = 600
PAN_US_MAX = 2400
PAN_US_CENTER = 1500

TILT_US_MIN = 600
TILT_US_MAX = 2400
TILT_US_CENTER = 1500

SERVO_UPDATE_S = 0.03  # 0.03–0.05 smoother
SERVO_KP_PAN = 0.25
SERVO_KP_TILT = 0.25
SERVO_MAX_STEP_US = 12  # 10–14

PAN_INVERT = False
TILT_INVERT = True

# ----------------------------
# Colour tracker cleanup (only used in colour mode)
# ----------------------------
MASK_KERNEL = (5, 5)
OPEN_ITERS = 1
CLOSE_ITERS = 1
CENTER_SMOOTH_ALPHA = 0.25
ERROR_SMOOTH_ALPHA = 0.25

# ----------------------------
# Distance (works after calibration click OR set focal below)
# ----------------------------
KNOWN_TARGET_WIDTH_CM = 16.0
CALIB_DISTANCE_CM = 50.0
FOCAL_LENGTH_PX = None
DIST_SMOOTH_ALPHA = 0.25

# ----------------------------
# Face tracking tuning
# ----------------------------
FACE_DETECT_SCALE = 0.5    # 0.5 good; 0.4 faster
FACE_CENTER_ALPHA = 0.25   # 0.15–0.35

FACE_CASCADE_PATH = None

# ==========================================================
# Local overrides (NOT tracked by git)
# Put your machine-specific settings in config_local.py
# ==========================================================
try:
    from config_local import *  # noqa
except ImportError:
    pass

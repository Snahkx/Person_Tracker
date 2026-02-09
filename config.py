# config.py
import numpy as np

# ----------------------------
# Camera
# ----------------------------
# If you want more detail, try (800, 600) or (960, 540).
# For best FPS, (640, 480).
PREVIEW_SIZE = (800, 600)

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

# Detection tuning (shared)
MIN_AREA = 1000

# Deadband: VERY important for servo stability (stops jitter)
DEADBAND_PX = 12  # try 10–20

# ----------------------------
# Mode: set to face for main goal
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

# Update speed (slower = smoother, less jitter)
SERVO_UPDATE_S = 0.03  # try 0.03–0.05

# Proportional gains (lower = smoother, higher = more aggressive)
SERVO_KP_PAN = 0.25
SERVO_KP_TILT = 0.25

# Cap movement per update (prevents violent swings)
SERVO_MAX_STEP_US = 12  # try 10–14

# Flip directions if tracking moves wrong way
PAN_INVERT = False
TILT_INVERT = True

# ----------------------------
# Vision cleanup (used by colour tracker)
# ----------------------------
MASK_KERNEL = (5, 5)
OPEN_ITERS = 1
CLOSE_ITERS = 1

# Generic smoothing (colour tracker uses these; face uses FACE_CENTER_ALPHA below)
CENTER_SMOOTH_ALPHA = 0.25
ERROR_SMOOTH_ALPHA = 0.25

# ----------------------------
# Distance calculations
# ----------------------------
# For face mode: KNOWN_TARGET_WIDTH_CM is "approx face width".
# Calibration makes this consistent for YOU.
KNOWN_TARGET_WIDTH_CM = 16.0
CALIB_DISTANCE_CM = 50.0
FOCAL_LENGTH_PX = None  # set after you click to calibrate
DIST_SMOOTH_ALPHA = 0.25

# ----------------------------
# Face detection tuning
# ----------------------------
# Detect on a smaller image then scale back up.
# Lower = faster but less accurate.
FACE_DETECT_SCALE = 0.5   # try 0.5, or 0.4 if still slow

# Smooth face center to reduce servo jitter
FACE_CENTER_ALPHA = 0.25  # try 0.15–0.35

# Optional override (leave None to use cv.data.haarcascades)
FACE_CASCADE_PATH = None

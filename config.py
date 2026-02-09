# Import libraries
import numpy as np

# Camera Size
PREVIEW_SIZE = (1280, 960)

# Change the colour that you want to track
# NOTE: Red wraps around hue=0, so we include both red bands for stability.
COLOR_RANGES = {
    "cb132b_red": [
        (
            np.array([0, 120, 60], dtype=np.uint8),    # Lower Bound (low red band)
            np.array([10, 255, 255], dtype=np.uint8),  # Upper Bound
        ),
        (
            np.array([170, 120, 60], dtype=np.uint8),  # Lower Bound (high red band)
            np.array([179, 255, 255], dtype=np.uint8), # Upper Bound
        ),
    ],
}

ACTIVE_COLORS = ["cb132b_red"]  # Changes the active colours

# Detection tuning
MIN_AREA = 1000   # Minimum area(px) of an object for detection
DEADBAND_PX = 0   # The error from the crosshair to the centre of the object

# Servo usage
USE_SERVO = True
TRACK_MODE = "colour"  # "person" | "colour" | "face"

# Servo pins
PAN_PIN = 18
TILT_PIN = 13

# ----------------------------
# pigpio servo settings (µs)
# ----------------------------
# Typical usable range is ~500–2500us, center ~1500us.
# You MUST tune these for your mount so you don't hit hard stops.
PAN_US_MIN = 600
PAN_US_MAX = 2400
PAN_US_CENTER = 1500

TILT_US_MIN = 600
TILT_US_MAX = 2400
TILT_US_CENTER = 1500

# How often to apply a servo update (seconds)
SERVO_UPDATE_S = 0.02

# Proportional tuning: converts pixel error -> microseconds change
# Bigger KP => more movement for the same error.
SERVO_KP_PAN = 0.35
SERVO_KP_TILT = 0.35

# Cap how much to change per update (microseconds)
SERVO_MAX_STEP_US = 16

# Flip directions if camera is mirrored or not
PAN_INVERT = False
TILT_INVERT = True

# Vision smoothing / cleanup
MASK_KERNEL = (10, 10)
OPEN_ITERS = 1
CLOSE_ITERS = 1
CENTER_SMOOTH_ALPHA = 1
ERROR_SMOOTH_ALPHA = 1

# Distance calculations
KNOWN_TARGET_WIDTH_CM = 16.0
CALIB_DISTANCE_CM = 50.0
FOCAL_LENGTH_PX = None  # computed when you press "c"
DIST_SMOOTH_ALPHA = 0.25

# Face cascade path (optional override)
# FACE_CASCADE_PATH = None

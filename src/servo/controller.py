# servo/controller.py
import time
import pigpio
import config
from servo.servos import Servo


def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))


class PanTiltController:
    """
    Mid-level control: error -> servo pulse width updates (pigpio).

    Changes vs your version:
    - Adds a "slow zone" so it moves fast when far away, but slows down near center
      to prevent overshoot/oscillation.
    - Keeps the same public API: update(error_x, error_y), close()
    """

    def __init__(self):
        self.pi = pigpio.pi()
        if not self.pi.connected:
            raise RuntimeError(
                "pigpio daemon not running (start with: sudo systemctl start pigpiod)"
            )

        self.pan = Servo(
            pi=self.pi,
            pin=config.PAN_PIN,
            us_min=config.PAN_US_MIN,
            us_max=config.PAN_US_MAX,
            us_center=config.PAN_US_CENTER,
        )

        self.tilt = Servo(
            pi=self.pi,
            pin=config.TILT_PIN,
            us_min=config.TILT_US_MIN,
            us_max=config.TILT_US_MAX,
            us_center=config.TILT_US_CENTER,
        )

        self._last_update = 0.0
        self._pan_acc = 0.0
        self._tilt_acc = 0.0


    def _scaled_max_step(self, error_x: int, error_y: int) -> float:
        mag = max(abs(error_x), abs(error_y))

        # Start fast when far
        scale = 1.2
        if mag > 250:
            scale = 1.6   # was 1.4
        elif mag > 150:
            scale = 1.2   # was 1.0
        elif mag > 80:
            scale = 0.7   # was 0.6
        else:
            scale = 0.40  # was 0.35
        return max(4, config.SERVO_MAX_STEP_US * scale)

    def update(self, error_x: int, error_y: int):
        now = time.time()
        if now - self._last_update < config.SERVO_UPDATE_S:
            return
        self._last_update = now

        if error_x == 0 and error_y == 0:
            return

        # Convert pixel error -> microsecond delta (proportional)
        d_pan = config.SERVO_KP_PAN * error_x
        d_tilt = config.SERVO_KP_TILT * error_y

        # Cap per update, with slow-zone scaling near center
        max_step = self._scaled_max_step(error_x, error_y)
        d_pan = clamp(d_pan, -max_step, max_step)
        d_tilt = clamp(d_tilt, -max_step, max_step)

        # Direction flips
        if config.PAN_INVERT:
            d_pan = -d_pan
        if config.TILT_INVERT:
            d_tilt = -d_tilt

        # Apply: subtracting generally moves toward reducing error
        # Accumulate fractional deltas so tiny movements still happen
        self._pan_acc += d_pan
        self._tilt_acc += d_tilt

        step_pan = int(round(self._pan_acc))
        step_tilt = int(round(self._tilt_acc))

        self._pan_acc -= step_pan
        self._tilt_acc -= step_tilt

        self.pan.set_us(self.pan.us - step_pan)
        self.tilt.set_us(self.tilt.us - step_tilt)


    def close(self):
        self.pan.stop()
        self.tilt.stop()
        self.pi.stop()
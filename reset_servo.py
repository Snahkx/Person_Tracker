# reset_servos.py
import time
import pigpio
import config
from servo.servos import Servo


def main():
    pi = pigpio.pi()
    if not pi.connected:
        raise RuntimeError(
            "pigpio daemon not running. Start with:\n"
            "sudo systemctl start pigpiod"
        )

    try:
        # Create servo objects
        pan = Servo(
            pi=pi,
            pin=config.PAN_PIN,
            us_min=config.PAN_US_MIN,
            us_max=config.PAN_US_MAX,
            us_center=config.PAN_US_CENTER,
        )

        tilt = Servo(
            pi=pi,
            pin=config.TILT_PIN,
            us_min=config.TILT_US_MIN,
            us_max=config.TILT_US_MAX,
            us_center=config.TILT_US_CENTER,
        )

        print("[INFO] Resetting servos to center...")

        # Explicitly set to center (in case they drifted)
        pan.set_us(config.PAN_US_CENTER)
        tilt.set_us(config.TILT_US_CENTER)

        # Give servos time to physically move
        time.sleep(0.8)

    finally:
        # Stop pulses so servos don't buzz
        pan.stop()
        tilt.stop()
        pi.stop()
        print("[INFO] Servos reset and released.")


if __name__ == "__main__":
    main()

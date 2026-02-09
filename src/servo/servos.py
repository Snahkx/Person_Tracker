# servo/servos.py
import pigpio

def clamp(v, vmin, vmax):
    return max(vmin, min(vmax, v))

class Servo:
    """
    Low-level pigpio servo driver.
    Uses pulse width in microseconds (µs).
    """

    def __init__(self, pi: pigpio.pi, pin: int, us_min: int, us_max: int, us_center: int):
        self.pi = pi
        self.pin = pin
        self.us_min = int(us_min)
        self.us_max = int(us_max)
        self.us = int(us_center)

        # Start at center
        self.set_us(self.us)

    def set_us(self, us: int):
        self.us = int(clamp(us, self.us_min, self.us_max))
        self.pi.set_servo_pulsewidth(self.pin, self.us)

    def stop(self):
        # 0 disables servo pulses
        self.pi.set_servo_pulsewidth(self.pin, 0)

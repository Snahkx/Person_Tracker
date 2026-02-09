# Import Libraries
from picamera2 import Picamera2
import cv2 as cv
import config

# Class for the camera
class Camera:
    def __init__(self):
        # Configure the camera into a class
        self.picam2 = Picamera2()
        # Configure the output size
        self.picam2.configure(
            self.picam2.create_preview_configuration(
                main={"size": config.PREVIEW_SIZE}
            )
        )
        # Start the camera
        self.picam2.start()

    # Call this everytime you need to capture an image from the camera
    def read(self):
        # Asks the camera for the most recent frame
        frame = self.picam2.capture_array()
        # If the frame is RGBA convert to BGR
        if frame.ndim == 3 and frame.shape[2] == 4:
            return cv.cvtColor(frame, cv.COLOR_RGBA2BGR)
        return cv.cvtColor(frame, cv.COLOR_RGB2BGR)

    # Closing function
    def close(self):
        self.picam2.stop()
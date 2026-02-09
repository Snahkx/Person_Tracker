# src/vision/tracker.py
from .colour_tracker import ColourTracker
from .person_tracker import PersonTracker
from .face_tracker import FaceTracker

def make_tracker(mode: str):
    mode = (mode or "").lower()

    if mode == "colour":
        return ColourTracker()
    if mode == "person":
        return PersonTracker()
    if mode == "face":
        return FaceTracker()

    raise ValueError(f"Unknown TRACK_MODE: {mode}")

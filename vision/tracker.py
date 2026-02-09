# vision/tracker.py
from vision.colour_tracker import ColourTracker

def make_tracker(mode: str):
    mode = (mode or "").lower()

    if mode == "colour":
        return ColourTracker()

    if mode == "person":
        from vision.person_tracker import PersonTracker
        return PersonTracker()

    if mode == "face":
        from vision.face_tracker import FaceTracker
        return FaceTracker()

    raise ValueError(f"Unknown TRACK_MODE: {mode}")

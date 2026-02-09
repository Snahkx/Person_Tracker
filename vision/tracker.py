# vision/tracker.py

from vision.colour_tracker import ColourTracker

def make_tracker(mode: str = None):
    # Force colour for now, ignore mode
    return ColourTracker()


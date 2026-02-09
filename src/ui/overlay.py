# Import libraries
import cv2 as cv

# Crosshair in the middle of the screen
def draw_crosshair(frame_bgr, size=20, thickness=2):
    H, W = frame_bgr.shape[:2]
    # Use open cv to create the crosshair
    cv.drawMarker(
        frame_bgr,
        (W // 2, H // 2), # Centres the crosshair
        (255, 255, 255),
        markerType=cv.MARKER_CROSS,
        markerSize=size,
        thickness=thickness,
    )

# Tracks the object
def draw_tracking_overlay(frame_bgr, result):
    # If theres no object dont display the overlay
    if not result.get("found", False):
        return

    # Gets the bounding box
    bbox = result.get("bbox")
    
    # Gets the center of the object
    center = result.get("center")
    # If there is no bounding box or no center
    if bbox is None or center is None:
        return

    # Gets the dimensions of the bbox
    x, y, w, h = bbox
    # Use the raw centre if found or fall back to the regular centre
    cx, cy = result.get("raw_center", result["center"])
    # Displays the shapes
    cv.rectangle(frame_bgr, (x, y), (x + w, y + h), (0, 255, 0), 2)
    cv.circle(frame_bgr, (cx, cy), 6, (255, 0, 0), -1)


    dist_cm = result.get("distance_cm", None)
    if dist_cm is not None:
        cv.putText(
            frame_bgr,
            f"{dist_cm:.1f} cm",
            (x, y + h + 25),
            cv.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )

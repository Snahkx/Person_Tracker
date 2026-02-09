# Distance Estimation (Monocular)

This document describes how `DistanceEstimator` estimates the distance between
the camera and a tracked target using a **single monocular camera**. The approach
uses a pinhole camera approximation, one-time calibration, and exponential
smoothing for real-time stability.

---

## Signal Processing Pipeline

Goal: estimate distance to target (cm) from a detected bounding box width (px).

Camera Frame
↓
Target Detection / Tracking
↓
Bounding Box Width (px)
↓
Pinhole Distance Model
↓
Exponential Smoothing
↓
Distance Estimate (cm)


---

## Core Model: Pinhole Camera Approximation

The estimator assumes a pinhole camera model where the apparent width of an
object in the image is inversely proportional to its distance from the camera.

distance_cm = (known_width_cm * focal_length_px) / bbox_width_px


Where:
- `known_width_cm` = real-world width of the target (KNOWN_TARGET_WIDTH_CM)
- `focal_length_px` = camera focal length in pixel units (FOCAL_LENGTH_PX)
- `bbox_width_px` = observed bounding box width in pixels

Interpretation:
- Larger bounding box → target is closer
- Smaller bounding box → target is farther

---

## Calibration (Estimating Focal Length in Pixels)

Because focal length in pixel units depends on camera intrinsics and resolution,
it is estimated once using a known-distance calibration.

focal_length_px = (bbox_width_px * calib_distance_cm) / known_width_cm

Where:
- `calib_distance_cm` = known distance during calibration (CALIB_DISTANCE_CM)
- `bbox_width_px` = bounding box width measured at that distance
- `known_width_cm` = real-world target width

---

### Practical Calibration Procedure

1. Place the target at a known distance (e.g. 50 cm).
2. Run the tracker and measure `bbox_width_px`.
3. Call `calibrate(bbox_width_px)` once.
4. Store the resulting `FOCAL_LENGTH_PX` in the config for repeatable runs.

---

### Notes / Assumptions

- Assumes the target’s effective width is consistent and roughly planar to the camera.
- Changing camera resolution changes pixel focal length.
- Recalibrate if camera resolution or lens changes.

---

## Distance Estimation (Runtime)

Once calibrated, distance is computed every frame using the pinhole model:

raw_distance_cm = (known_width_cm * focal_length_px) / bbox_width_px


If focal length is unknown or `bbox_width_px <= 0`, the estimator returns `None`
to avoid invalid results.

---

## Smoothing (Low-Pass Filter)

Raw distance estimates fluctuate due to detection noise (lighting, occlusion,
bounding box jitter). To stabilize the output, exponential smoothing is applied.

smoothed_distance =
(1 - alpha) * previous_distance + alpha * current_distance


Where:
- `alpha` = smoothing factor (DIST_SMOOTH_ALPHA)
- Lower alpha → smoother but slower response
- Higher alpha → faster response but noisier

Implementation detail:
- On the first valid estimate, the smoothed value is initialized directly.

---

## Configuration Reference

| Parameter | Config Key | Default | Description |
|---------|-----------|---------|-------------|
| Target width (cm) | KNOWN_TARGET_WIDTH_CM | 16.0 | Assumed real-world target width |
| Calibration distance (cm) | CALIB_DISTANCE_CM | 50.0 | Known distance for calibration |
| Focal length (px) | FOCAL_LENGTH_PX | None | Computed once via calibration |
| Smoothing factor | DIST_SMOOTH_ALPHA | 0.25 | Exponential smoothing strength |

---

## Failure Conditions

The estimator returns `None` when:
- Focal length has not been calibrated
- Bounding box width is zero or invalid

This prevents divide-by-zero and meaningless distance values.

---

## Limitations

- Distance accuracy depends on the correctness of `known_width_cm`
- Bounding box width changes with target orientation (e.g. rotation)
- Monocular depth estimation is inherently approximate
- Not suitable for precise ranging or safety-critical decisions

Despite these limitations, the estimator provides a lightweight and
real-time distance approximation suitable for visualization and
coarse behavior logic.

---

## Future Improvements

- Height-based estimation (more stable for upright people)
- Keypoint-based distance instead of bounding box width
- Kalman filtering for predictive smoothing
- Multi-point calibration curve

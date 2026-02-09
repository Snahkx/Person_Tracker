# Distance Estimation (Monocular) — Pinhole Model Notes

This document explains how `distance.estimator.DistanceEstimator` estimates the target’s distance
from a **single camera** using the **pinhole camera model**, plus the calibration and smoothing used
to make it stable in real-time tracking.

---

## Signal Processing Pipeline (Distance)

**Goal:** estimate distance-to-target (cm) from a detected bounding box width (px).

---

Camera Frame → Detection/Tracking → Bounding Box Width (px)
↓
Calibration (once)
↓
Pinhole Distance Estimate (cm) → Smoothing → Display / Control

---

### Inputs
- `bbox_width_px`: width of the detected bounding box in pixels (from vision tracker)
- `KNOWN_TARGET_WIDTH_CM`: assumed real-world width of the target (defaults to `16.0 cm`)
- `CALIB_DISTANCE_CM`: known distance used during calibration (defaults to `50.0 cm`)
- `FOCAL_LENGTH_PX`: focal length in pixel units (either pre-set or computed via calibration)
- `DIST_SMOOTH_ALPHA`: smoothing factor (defaults to `0.25`)

### Output
- Estimated distance in **cm** (smoothed), or `None` if not enough info is available.

---

## Core Model: Pinhole Camera Approximation

We model the camera as a pinhole camera. For an object of known real width:

\[
\text{distance}_{cm} = \frac{W_{cm} \cdot f_{px}}{w_{px}}
\]

Where:
- \( W_{cm} \) = known real-world target width in cm (`KNOWN_TARGET_WIDTH_CM`)
- \( f_{px} \) = focal length in pixels (`FOCAL_LENGTH_PX`)
- \( w_{px} \) = bounding box width in pixels (`bbox_width_px`)

**Interpretation:**  
If the bounding box appears **larger** (bigger \( w_{px} \)), the target is **closer** (smaller distance).  
If the bounding box appears **smaller**, the target is **farther**.

---

## Calibration (Estimating \( f_{px} \))

Because camera focal length in **pixel units** depends on resolution and camera intrinsics, we estimate
\( f_{px} \) once using a simple one-point calibration:

\[
f_{px} = \frac{w_{px} \cdot D_{cm}}{W_{cm}}
\]

Where:
- \( D_{cm} \) = known calibration distance (`CALIB_DISTANCE_CM`)
- \( w_{px} \) = observed bounding box width at that distance
- \( W_{cm} \) = known target width

### Practical Calibration Procedure
1. Place the target at a known distance (ex: **50 cm**).
2. Run tracking and measure `bbox_width_px`.
3. Call `calibrate(bbox_width_px)` once.
4. Save the resulting `FOCAL_LENGTH_PX` into your config for repeatable runs.

### Notes / Assumptions
- This assumes the target’s effective width is consistent and roughly planar to the camera.
- Changing camera resolution changes the pixel focal length; recalibrate if you change resolution.

---

## Smoothing (Low-Pass Filter)

Raw distance estimates fluctuate because detection output fluctuates (lighting, occlusion, bounding box jitter).
To stabilize it in real time, we apply exponential smoothing:

\[
\hat{d}_t = (1-\alpha)\hat{d}_{t-1} + \alpha d_t
\]

Where:
- \( d_t \) = raw distance estimate at time \( t \)
- \( \hat{d}_t \) = smoothed distance estimate
- \( \alpha \) = smoothing factor (`DIST_SMOOTH_ALPHA`)

**Behavior:**
- Lower \( \alpha \) (e.g., 0.10) → smoother but slower response
- Higher \( \alpha \) (e.g., 0.40) → faster response but noisier

Implementation detail:
- On the first valid measurement, the smoothed estimate is initialized directly to that value.

---

## Failure Conditions / Guardrails

The estimator returns `None` if:
- `FOCAL_LENGTH_PX` is not known (not calibrated and not provided)
- `bbox_width_px <= 0`

This prevents divide-by-zero and prevents displaying meaningless distance values.

---

## Configuration Reference

These are the config keys used (defaults shown):

| Parameter | Config Key | Default | Meaning |
|----------|------------|---------|--------|
| Target width (cm) | `KNOWN_TARGET_WIDTH_CM` | 16.0 | Real-world width assumption |
| Calibration distance (cm) | `CALIB_DISTANCE_CM` | 50.0 | Known distance used to compute focal length |
| Focal length (px) | `FOCAL_LENGTH_PX` | None | Pixel focal length; computed via calibration |
| Smoothing alpha | `DIST_SMOOTH_ALPHA` | 0.25 | Exponential smoothing strength |

---

## Implementation Snippet (for reference)

The estimator follows this structure:

- `calibrate(bbox_width_px)` computes and stores `focal_px`
- `estimate_cm(bbox_width_px)` returns a smoothed distance estimate

If you want deterministic runs, calibrate once, then store `FOCAL_LENGTH_PX` in config.

---

## Limitations (Important)

This method is intentionally simple and fast, but it has limitations:

- **Assumed target width:** distance accuracy depends on how well `KNOWN_TARGET_WIDTH_CM`
  matches the true target width in the scene.
- **Perspective effects:** if the target rotates (shoulders angled), apparent width shrinks,
  which looks like “farther away.”
- **Bounding box instability:** detection jitter directly affects distance jitter.
- **Monocular ambiguity:** depth from a single camera is inherently approximate.

Despite these limitations, it provides a useful real-time estimate suitable for display,
basic behavior logic, or coarse distance-aware control.

---

## Suggested Future Improvements

- Use height-based estimation (more stable for upright people)
- Use a tracked keypoint distance (e.g., shoulder keypoints) instead of bbox width
- Apply a Kalman filter for smoother prediction
- Calibrate using multiple points (distance vs bbox size curve)

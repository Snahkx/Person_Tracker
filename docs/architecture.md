# System Architecture

This document describes the high-level architecture of the real-time
vision-based tracking system, including subsystem boundaries, data flow,
and design rationale.

The system was intentionally structured to separate perception, control,
and hardware interaction, allowing each layer to be developed, tested,
and reasoned about independently.

---

## High-Level Overview

At a high level, the system operates as a closed-loop feedback controller:

1. Capture a video frame from the camera
2. Detect and localize a target in image space
3. Compute positional error relative to the image center
4. Convert error into pan–tilt motion commands
5. Actuate servos to reorient the camera
6. Repeat at real-time frequency

This loop runs continuously on Raspberry Pi hardware.

---

## Subsystem Decomposition

The system is divided into three primary subsystems:

- Vision Pipeline
- Control Layer
- Hardware Interface

Each subsystem has a clearly defined responsibility and communicates
through simple, explicit interfaces.

---

## Vision Pipeline

**Responsibility:**  
Convert raw camera frames into a target position in pixel coordinates.

**Key components:**
- Camera abstraction for frame acquisition
- Detection modules (person / face / colour)
- Target selection and bounding box extraction
- Overlay rendering for diagnostics

The vision pipeline outputs:
- Target centroid `(x, y)` in image space
- Bounding box dimensions
- A validity signal indicating whether a target is currently tracked

The pipeline is designed to be stateless between frames, which simplifies
debugging and allows tracking modes to be swapped without affecting
downstream control logic.

---

## Control Layer

**Responsibility:**  
Translate image-space error into stable, physically safe servo commands.

The control layer receives:
- Horizontal and vertical pixel error
- Target validity state

It outputs:
- Pan and tilt servo pulse-width updates

### Error Computation

Error is computed as the difference between the target centroid and the
image center. This representation is intuitive, camera-agnostic, and
directly maps to pan–tilt motion.

### Deadband Logic

A configurable deadband is applied around the image center to suppress
small corrections caused by detection noise. This prevents servo jitter
and oscillation when the target is already approximately centered.

### Rate Limiting and Smoothing

To avoid aggressive motion when the target is far from center, the control
layer scales movement based on error magnitude. Large errors result in
faster motion, while small errors result in slower, finer adjustments.

---

## Hardware Interface

**Responsibility:**  
Safely translate control commands into physical motion.

The hardware interface:
- Initializes the pigpio connection
- Configures servo pulse-width limits
- Enforces minimum and maximum travel bounds
- Provides a clean shutdown path

Hardware availability is treated as a runtime condition rather than a
compile-time assumption. If the pigpio daemon is unavailable, the system
fails gracefully without crashing the vision pipeline.

---

## Configuration Strategy

All tunable parameters (servo limits, deadband size, detection thresholds)
are centralized in configuration files.

This approach:
- Eliminates hard-coded constants
- Enables rapid tuning without code changes
- Allows environment-specific overrides
- Makes system behavior explicit and auditable

---

## Data Flow Summary
## Architecture Diagram (End-to-End)

```text
┌───────────────────────────────────────────────────────────────┐
│                         Operator / User                        │
│  - Launches runtime (python main.py)                           │
│  - Observes overlay + tuning feedback                          │
└───────────────────────────────────────────────────────────────┘
                          │  Launch / Config
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                       Runtime: main.py                         │
│  Application Loop:                                              │
│  - frame = Camera.read()                                        │
│  - result = tracker.process(frame)                              │
│  - compute pixel error vs frame center                          │
│  - update PanTiltController (if enabled)                        │
│  - draw overlay diagnostics                                     │
└───────────────────────────────────────────────────────────────┘
                          │  Frame + detection results
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                    Vision Subsystem (src/vision)               │
│  Camera                                                        │
│  - Pi Camera / USB capture                                     │
│  - resolution + FPS tuning                                     │
│                                                               │
│  Trackers (person / face / colour)                              │
│  - detection + bounding box extraction                          │
│  - target selection (single target)                             │
│  - outputs centroid (x,y), bbox, valid flag                     │
└───────────────────────────────────────────────────────────────┘
                          │  Pixel error (dx, dy)
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                 Control Subsystem (src/servo)                  │
│  PanTiltController                                              │
│  - deadband (jitter suppression near center)                    │
│  - error → step/velocity mapping                                │
│  - rate limiting / smoothing for stability                      │
│  - enforces min/max pulse widths (safe bounds)                  │
│                                                               │
│  pigpio Interface                                               │
│  - connects to pigpio daemon                                    │
│  - sends PWM pulse widths to GPIO pins                          │
└───────────────────────────────────────────────────────────────┘
                          │  PWM (pulse width in µs)
                          ▼
┌───────────────────────────────────────────────────────────────┐
│                        Hardware Platform                        │
│  Pan Servo (Yaw)                 Tilt Servo (Pitch)             │
│  - horizontal rotation           - vertical rotation             │
│             \                         /                          │
│              \                       /                           │
│               ▼                     ▼                            │
│               Pan–Tilt Mechanical Assembly                       │
│        (SolidWorks CAD + drawings in /hardware)                  │
│                               │                                 │
│                               ▼                                 │
│                           Camera Mount                           │
└───────────────────────────────────────────────────────────────┘


---

### Interface Contracts (What each layer guarantees)

- Vision → Control:
  - Provides `(dx, dy)` pixel error from frame center and a `valid` flag.
  - Guarantees coordinates are in image space using the same frame resolution.

- Control → Hardware:
  - Provides bounded PWM pulse widths (µs) for pan and tilt channels.
  - Guarantees safety limits are enforced before commanding servos.

- Hardware → Vision:
  - Motion changes camera orientation; vision loop compensates continuously.
  - No direct feedback from servos is assumed (open-loop actuation).

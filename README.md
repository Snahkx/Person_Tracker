# Real-Time Vision-Based Person Tracking with Pan–Tilt Control

This project is a hands-on exploration of real-time computer vision,
embedded control, and mechanical design. The system detects a human target
in a camera feed and physically reorients the camera using a pan–tilt
mechanism to keep the target centered.

It was built as an end-to-end system: from camera input, through control
logic, all the way to custom hardware.

---

## Why This Project Exists

I wanted to build something that closed the loop between perception and
physical motion. Rather than stopping at detection on a screen, this
project forces the software to deal with the messiness of real hardware:
noise, latency, jitter, and failure modes.

The goal was not perfection, but understanding.

---

## What the System Does

- Captures live video on a Raspberry Pi
- Detects and tracks a human target
- Computes image-space error relative to the frame center
- Converts that error into pan–tilt servo commands
- Physically moves the camera to follow the target

All of this runs in real time on embedded hardware.

---

## System Structure

The system is organized into three layers:
- Vision (what do I see?)
- Control (how should I move?)
- Hardware (how do I move safely?)

Each layer is deliberately kept simple and isolated.

For details, see:
- [`docs/architecture.md`](docs/architecture.md)
- [`docs/design-decisions.md`](docs/design-decisions.md)

---

## Hardware

The camera is mounted on a custom-designed pan–tilt platform modeled in
SolidWorks. The design focuses on alignment, stiffness, and ease of
iteration using 3D-printed components.

📁 Hardware CAD, drawings, and BOM: [`hardware/`](hardware/)

---

## Validation

The system was tested on physical Raspberry Pi hardware with a servo-driven
pan–tilt platform. Testing focused on:
- Stability near the image center
- Smooth target reacquisition
- Safe behavior during target loss

---

## Current State

The core system is complete and documented. Demo media and annotated
screenshots will be added once hardware access is available.

---

## Future Directions

This project is intentionally extensible. Possible next steps include:
- Predictive filtering for smoother motion
- Multi-target tracking
- ROS2 integration
- Hardware acceleration for vision processing

---

## Repo Guide

- `src/` – vision, control, and runtime code  
- `hardware/` – CAD, drawings, and BOM  
- `docs/` – architecture and design documentation  
- `demo/` – demo media (to be added)

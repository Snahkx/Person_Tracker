# Real-Time Vision-Based Person Tracking with Pan–Tilt Control

A Raspberry Pi–based computer vision system that detects and tracks a human target
in real time and drives a two-axis pan–tilt servo platform to maintain target centering.

This project integrates computer vision, embedded control, and custom mechanical
design into a closed-loop tracking system intended as a compact robotics platform
for experimentation and learning.

---

## Overview

The goal of this project was to design and implement an end-to-end tracking system
capable of detecting a person in a camera feed and physically reorienting the camera
to keep the target centered. The system processes video frames on a Raspberry Pi,
estimates positional error relative to the image center, and converts that error
into servo commands that actuate a pan–tilt mechanism.

The software is modular, configuration-driven, and designed to degrade gracefully
in the absence of hardware dependencies, allowing development and testing to proceed
without constant access to physical components.

---

## System Architecture

The system is composed of three primary subsystems:

### 1. Vision Pipeline
- Camera capture and frame preprocessing
- Target detection (person / face / colour modes)
- Bounding box extraction and target selection
- Pixel-space error computation relative to frame center

### 2. Control Layer
- Error-to-motion conversion
- Deadband logic to suppress jitter near the target center
- Rate limiting and smoothing to prevent oscillation
- Servo pulse-width generation via pigpio

### 3. Hardware Platform
- Two-axis pan–tilt mechanism driven by hobby servos
- Camera rigidly mounted to maintain optical alignment
- Raspberry Pi acting as both compute and control unit

The architecture cleanly separates perception, control, and hardware concerns,
allowing individual subsystems to be modified or replaced with minimal impact
on the rest of the system.

---

## Key Features

- Real-time person and face tracking using OpenCV
- Closed-loop pan–tilt servo control based on image-space error
- Deadband-based jitter suppression near the target center
- Modular tracking modes (person, face, colour)
- Centralized configuration for tuning control and detection parameters
- Hardware-safe initialization and shutdown behavior
- Graceful failure handling when hardware dependencies are unavailable

---

## Engineering Challenges & Solutions

### Servo Jitter Near Target Center
Small detection noise caused rapid micro-adjustments when the target was near the
center of the frame. This was mitigated by introducing a configurable deadband,
preventing corrective motion unless the error exceeded a minimum threshold.

### Noisy Detections Under Variable Conditions
Detection output fluctuated due to lighting changes and partial occlusions.
Minimum-area filtering and target reacquisition logic were used to stabilize tracking
and reduce false corrections.

### Hardware Dependency Management
The pigpio daemon is required for servo control. Runtime checks were added to detect
daemon availability and prevent unsafe behavior when the dependency is missing,
allowing the system to run in a vision-only mode.

### Performance Constraints on Raspberry Pi
To maintain real-time responsiveness, resolution, processing frequency, and pipeline
complexity were tuned to balance detection accuracy and frame rate.

---

## Validation & Testing

The system was validated through live testing on physical Raspberry Pi hardware:

- Verified real-time target detection and continuous tracking
- Confirmed stable pan–tilt motion under typical indoor conditions
- Observed reduced oscillation near the image center due to deadband control
- Confirmed safe behavior during target loss and reacquisition

---

## Hardware Design

The camera is mounted on a custom-designed pan–tilt platform modeled in SolidWorks.
The mechanical design prioritizes stiffness, alignment, and serviceability while
remaining compact and easy to manufacture via 3D printing.

📁 Hardware CAD, drawings, and BOM: [`hardware/`](hardware/)

---

## Project Status

Demo media and annotated screenshots will be added once hardware access is available.
The system architecture, control logic, and mechanical design are complete and documented.

---

## Future Work

- Kalman filtering for smoother tracking and prediction
- Multi-target detection and selection logic
- ROS2 node integration for broader robotics use
- Edge acceleration using dedicated vision hardware (TPU / NPU)

---

## Repo Tour

- `src/vision/` – camera handling and detection pipeline  
- `src/servo/` – pan–tilt control and safety logic  
- `src/ui/` – overlay rendering and diagnostics  
- `hardware/` – CAD, drawings, and bill of materials  
- `docs/` – engineering report and design documentation  
- `demo/` – demo media (to be added)


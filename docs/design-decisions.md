# Design Decisions & Rationale

This document captures the key design decisions made during development,
including alternatives considered and tradeoffs accepted.

The goal is not to claim optimality, but to document reasoning.

---

## Choice of Platform: Raspberry Pi

The Raspberry Pi was selected as the target platform due to:
- Widespread availability
- Adequate performance for real-time vision tasks
- Direct GPIO access for servo control
- Strong ecosystem support
- Beginner introduction to bash, linux, and terminal cmds

Resource constraints influenced several downstream design decisions,
particularly around processing frequency and algorithm complexity.

---

## Vision Library: OpenCV

OpenCV was chosen for its:
- Mature and well-documented API
- Real-time performance on ARM platforms
- Broad support for classical vision techniques
- Ease of integration with Python
- Default Libraries

Deep learning–based detectors were intentionally avoided in the initial
implementation to reduce system complexity and hardware dependency.

---

## Control Strategy: Classical Feedback Control

A classical feedback control approach was chosen over more advanced
predictive methods.

Reasons:
- Transparent behavior that is easy to reason about
- Minimal tuning complexity
- Robustness to partial or noisy detections
- Suitability for low-latency embedded systems

This decision favored reliability and interpretability over theoretical
optimality.

---

## Deadband-Based Stabilization

Initial testing revealed servo jitter when the target hovered near the
image center. Rather than filtering detection output aggressively, a
deadband was introduced at the control level.

This approach:
- Directly addresses the symptom (micro-corrections)
- Preserves responsiveness for larger errors
- Simplifies tuning

---

## pigpio for Servo Control

pigpio was selected instead of software PWM due to:
- Hardware-timed pulse generation
- Reduced jitter under system load
- Precise pulse-width control

The dependency on a background daemon was accepted in exchange for
improved control stability.

---

## Modular Tracking Modes

Tracking modes (person, face, colour) were implemented as modular units
sharing a common interface.

This decision:
- Simplifies experimentation
- Avoids entangling detection logic with control logic
- Enables rapid switching without structural changes

---

## Configuration-Driven Design

Centralized configuration files were used to avoid embedding tuning
parameters directly in code.

Benefits:
- Faster iteration during testing
- Clear separation between logic and parameters
- Easier portability across hardware setups

---

## Error Handling Philosophy

Rather than failing loudly when hardware components are unavailable,
the system degrades gracefully.

This reflects a practical development reality: hardware is not always
available, but software iteration should continue regardless.

---

## Known Limitations

- No predictive tracking or velocity estimation
- Single-target assumption
- Limited robustness under extreme lighting conditions

These limitations were consciously accepted to prioritize system clarity
and stability.

---

## Reflection

Many of these decisions prioritize understandability and robustness over
maximum performance. This aligns with the project’s goal as a learning
platform and a foundation for future expansion rather than a production
deployment.

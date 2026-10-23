# Architecture Overview

PS5-REMOTE-PLAY is intentionally designed as a modular, from-scratch client with a strong bias toward running on older or constrained hardware.

## High-Level Layers

1. **Discovery & Registration**
   - Local network discovery of PS4/PS5 consoles
   - Manual host addition
   - Console registration using the 8-byte little-endian base64 PSN Account ID + PIN
   - Session key exchange

2. **Session / Control Protocol**
   - Handshake and control channel (independent of video)
   - Heartbeats, resolution / bitrate negotiation
   - Input packet transmission

3. **Streaming Pipeline (Video + Audio)**
   - Receive encrypted H.264 / H.265 streams
   - Prefer **software decoding** first (libavcodec / FFmpeg software path)
   - Optional hardware acceleration when available, but never required
   - Configurable resolution and bitrate ceilings for weak machines

4. **Input**
   - Keyboard / mouse / gamepad abstraction
   - DualShock / DualSense mapping where possible
   - Low-latency path prioritised

5. **UI**
   - Lightweight, preferably immediate-mode or minimal retained-mode UI
   - Should remain usable on low-DPI / older displays

## Design Principles for Older Hardware

- Software decode is first-class, not a fallback
- Aggressive frame dropping and resolution downscaling options
- Minimal dependencies outside of well-supported libraries (FFmpeg, a small networking stack, a light UI toolkit)
- Avoid heavy frameworks that pull in modern GPU requirements
- Clear compile-time and runtime feature flags so users can strip expensive paths

## Independence

This codebase does not import, copy, or derive from Chiaki, chiaki-ng, pyremoteplay, or any other existing Remote Play client. Protocol understanding is being re-implemented independently.

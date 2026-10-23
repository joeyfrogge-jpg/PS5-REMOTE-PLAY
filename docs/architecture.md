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

3. **Streaming Pipeline (Video + Audio)** – *implemented skeleton*
   - `src/stream/receiver.py` – Async UDP receiver with large buffers
   - `src/stream/crypto.py` – Decryption interface (AES placeholder, ready for real keys)
   - `src/stream/decoder.py` – Software-first H.264/H.265 + audio decoder via PyAV/FFmpeg
   - `src/stream/pipeline.py` – Orchestrator that wires the stages together
   - `src/stream/config.py` – Conservative defaults aimed at older hardware

4. **Input**
   - Keyboard / mouse / gamepad abstraction
   - DualShock / DualSense mapping where possible
   - Low-latency path prioritised

5. **UI**
   - Lightweight, preferably immediate-mode or minimal retained-mode UI
   - Should remain usable on low-DPI / older displays

## Streaming Pipeline Flow

```
UDP datagram
    → StreamReceiver
        → StreamCrypto.decrypt()
            → simple demux (payload type)
                → StreamDecoder (software path preferred)
                    → video/audio frame callbacks (for renderer)
```

## Design Principles for Older Hardware

- Software decode is first-class, not a fallback
- Aggressive frame dropping and resolution downscaling options
- Minimal dependencies outside of well-supported libraries (FFmpeg via PyAV, cryptography)
- Avoid heavy frameworks that pull in modern GPU requirements
- Clear runtime configuration so users can force low-power modes

## Independence

This codebase does not import, copy, or derive from Chiaki, chiaki-ng, pyremoteplay, or any other existing Remote Play client. Protocol understanding is being re-implemented independently.

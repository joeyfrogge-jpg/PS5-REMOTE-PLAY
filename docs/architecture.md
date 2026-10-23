# Architecture Overview

PS5-REMOTE-PLAY is a modular, from-scratch client with a strong bias toward older / constrained hardware.

## High-Level Layers

1. **Protocol Layer** (`src/protocol/`)
   - `discovery.py` – Local network console discovery
   - `registration.py` – Registration using base64 PSN Account ID + PIN
   - `session.py` – Session lifecycle, control channel, ties into the streaming pipeline

2. **Streaming Pipeline** (`src/stream/`)
   - `receiver.py` – Async UDP media receiver
   - `crypto.py` – Decryption interface
   - `decoder.py` – Software-first H.264/H.265 + audio (PyAV)
   - `pipeline.py` – Orchestrator
   - `config.py` – Older-hardware friendly defaults

3. **Core** (`src/core/`)
   - `account.py` – base64 ↔ numeric Account ID helpers

4. **Application**
   - `main.py` – Dark-themed GUI that drives discovery → registration → session → stream

## Session Flow

```
User supplies Account ID (base64) + PIN
        ↓
Discovery (optional) → ConsoleInfo
        ↓
Registration (Account ID + PIN) → session key material
        ↓
Control channel opened
        ↓
StreamPipeline started (UDP listen port)
        ↓
Start-stream command sent on control channel
        ↓
Media packets → decrypt → decode → (future render)
```

## Design Principles

- Software decode is first-class
- Conservative resolution / bitrate defaults
- Clean public APIs so each layer can be completed independently
- No code derived from Chiaki or other existing clients

## Current Limitations

The high-level protocol flow and public interfaces are in place. Exact binary packet layouts for discovery, registration and control are still being independently finalized. Until those are complete, real console connections will not fully succeed.

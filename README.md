# PS5-REMOTE-PLAY

**Independent open-source PlayStation Remote Play client** for PS4 and PS5.

This is a **from-scratch** implementation focused on maximum compatibility with older / lower-powered hardware (older CPUs, integrated graphics, low-end laptops, single-board computers, and legacy operating systems). It is **not** a fork of Chiaki or any other existing project.

## Goals

- Full Remote Play experience equivalent to the official PlayStation Remote Play app
- Registration using your **PSN Account ID in base64** (the 8-byte little-endian base64 value)
- Strong emphasis on **older hardware compatibility**:
  - Software video decoding paths (no hard requirement for modern GPU decode)
  - Configurable low-resolution / low-bitrate modes
  - Lightweight UI that runs on modest systems
  - Support for older operating systems where practical
- Clean, modern, well-documented codebase that others can audit and extend
- Fully open source

## Status

This repository is the foundation of a new independent client. Core protocol work, streaming pipeline, and registration flow are under active development.

## Getting Your Base64 Account ID

Remote Play clients register with your console using your PSN Account ID (not your Online ID).  
It is an 8-byte little-endian integer encoded as base64.

You can obtain it with the included helper:

```bash
python tools/get_account_id.py
```

Or use any of the well-known public methods that extract the same value (the format is standard).

Paste the resulting base64 string into the client when registering a console.

## Building / Running (placeholder)

```bash
# Coming soon – current focus is core library and protocol implementation
```

## Project Structure

```
PS5-REMOTE-PLAY/
├── README.md
├── LICENSE
├── docs/
│   └── architecture.md
├── tools/
│   └── get_account_id.py          # Helper to obtain base64 Account ID
├── src/
│   ├── core/                      # Protocol, session, discovery
│   ├── stream/                    # Video/audio pipeline (software decode first)
│   ├── input/                     # Controller mapping
│   └── ui/                        # Lightweight frontend
└── tests/
```

## License

MIT License – see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Sony Interactive Entertainment in any way.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.  
This is an independent open-source effort for educational and personal use.

Use at your own risk. Streaming your own console is generally permitted under Sony’s terms when using official methods; third-party clients exist in a gray area of reverse-engineered protocols.

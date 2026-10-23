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

## Current Status

| Component              | Status                          |
|------------------------|---------------------------------|
| Account ID tooling     | Done                            |
| Streaming pipeline     | **Skeleton implemented**        |
| Software decoder       | Working (PyAV / FFmpeg)         |
| Packet receiver        | Working (async UDP)             |
| Stream crypto          | Interface ready (placeholder)   |
| Session / control      | Not started                     |
| Discovery / registration | Not started                   |
| Input & UI             | Not started                     |

### Streaming Pipeline Highlights

- `StreamPipeline` orchestrates receive → decrypt → demux → decode
- **Software decoding is the default** and first-class path
- Conservative defaults (720p / 30 fps / modest bitrate) for older machines
- Easy to force low-power mode via `StreamConfig`

## Getting Your Base64 Account ID

```bash
python tools/get_account_id.py
```

Paste the resulting base64 string when registering a console.

## Quick Start (development)

```bash
pip install -r requirements.txt

# Example of creating a pipeline (still needs a real session)
from src.stream import StreamPipeline, StreamConfig

config = StreamConfig(
    max_width=1280,
    max_height=720,
    target_fps=30,
    decode_mode="software"   # explicit
)
pipeline = StreamPipeline(config)
# await pipeline.start()
```

## Project Structure

```
PS5-REMOTE-PLAY/
├── README.md
├── LICENSE
├── requirements.txt
├── docs/
│   └── architecture.md
├── tools/
│   └── get_account_id.py
├── src/
│   ├── core/
│   │   └── account.py          # base64 Account ID helpers
│   └── stream/
│       ├── config.py           # older-hardware friendly settings
│       ├── receiver.py         # async UDP receiver
│       ├── crypto.py           # decryption interface
│       ├── decoder.py          # software-first PyAV decoder
│       └── pipeline.py         # main orchestrator
└── tests/
```

## License

MIT License – see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Sony Interactive Entertainment in any way.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.  
This is an independent open-source effort for educational and personal use.

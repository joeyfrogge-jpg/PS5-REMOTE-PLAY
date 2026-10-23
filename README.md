# PS5-REMOTE-PLAY

Independent open-source client for PlayStation Remote Play (PS4 & PS5).

Built from scratch with a focus on **older and lower-powered hardware** — software video decoding, modest default resolutions, and a lightweight desktop UI. This is **not** a fork of Chiaki or any other existing project.

> **Current stage:** The architecture, GUI, streaming pipeline, discovery, registration, and session layers are in place. Exact binary protocol packets are still being finalized, so reliable streaming from a real console is not yet available.

## Download the Windows .exe

### Every commit
The Windows `.exe` is built automatically on every push to `main`.

1. Open the **Actions** tab: https://github.com/joeyfrogge-jpg/PS5-REMOTE-PLAY/actions  
2. Select the latest successful **Build Windows Release** run  
3. Download the artifact **PS5-REMOTE-PLAY-windows**

Artifacts are kept for 30 days.

### Versioned Releases
Pushing a tag such as `v0.1.0` also creates a proper GitHub Release with the `.exe` attached:

https://github.com/joeyfrogge-jpg/PS5-REMOTE-PLAY/releases

---

## Features (implemented)

- PSN Account ID (base64) validation and helpers
- Local network console discovery
- Registration flow (Account ID + 8-digit PIN)
- Session lifecycle and control channel scaffolding
- Streaming pipeline: UDP receive → decrypt → software decode (H.264/H.265)
- Configurable resolution, FPS, bitrate, and decode mode
- Simple dark-themed desktop GUI
- One-click Windows build (`build.bat`) and automated CI builds

## Quick start (from source)

```bash
pip install -r requirements.txt
python main.py
```

1. Paste your base64 PSN Account ID and click **Validate**
2. Click **Discover** or enter the console IP manually
3. Enter the 8-digit PIN shown on the PlayStation
4. Choose resolution / FPS / decode settings
5. Press **Connect & Start Stream**

## Local Windows build

```bat
build.bat
```

The executable appears at `dist\PS5-REMOTE-PLAY.exe`.

## Project layout

```
PS5-REMOTE-PLAY/
├── main.py                          # Desktop GUI
├── build.bat                        # Local Windows builder
├── .github/workflows/               # CI – builds .exe on every commit
├── src/
│   ├── core/                        # Account ID helpers
│   ├── protocol/                    # Discovery, registration, session
│   └── stream/                      # Media pipeline (receive/decode)
├── tools/
│   └── get_account_id.py            # Helper to obtain base64 Account ID
└── docs/
    └── architecture.md
```

## License

MIT – see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Sony Interactive Entertainment.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.  
Use at your own risk.

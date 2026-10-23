# PS5-REMOTE-PLAY

**Independent open-source PlayStation Remote Play client** for PS4 and PS5.

This is a **from-scratch** implementation focused on maximum compatibility with older / lower-powered hardware. It is **not** a fork of Chiaki or any other existing project.

## Current Status

| Component                | Status                          |
|--------------------------|---------------------------------|
| Account ID tooling       | Done                            |
| Streaming pipeline       | Skeleton implemented            |
| Software decoder         | Working (PyAV / FFmpeg)         |
| Packet receiver          | Working (async UDP)             |
| Stream crypto            | Interface ready (placeholder)   |
| Desktop GUI launcher     | **Done**                        |
| Windows .exe packaging   | **Ready** (see below)           |
| Session / control        | Not started                     |
| Discovery / registration | Not started                     |
| Real console connection  | Not yet possible                |

> **Important**: This is still a development skeleton. The .exe runs and exercises the streaming pipeline layers, but it **cannot yet connect to a real PS4/PS5**. Full protocol implementation is required before that works.

## Build the Windows .exe

### Requirements
- Windows 10 or 11
- Python 3.10 or newer (https://www.python.org)
- Make sure “Add Python to PATH” was checked during installation

### One-click build

1. Download or clone this repository
2. Double-click **`build.bat`**
3. Wait for it to finish
4. Your executable will be at:

```
dist\PS5-REMOTE-PLAY.exe
```

You can copy that single `.exe` anywhere and run it. No Python installation is required on the target machine.

### Manual build (alternative)

```bat
pip install -r requirements.txt
pyinstaller --noconfirm --clean --onefile --windowed --name "PS5-REMOTE-PLAY" --add-data "src;src" main.py
```

Or use the provided spec file:

```bat
pyinstaller --noconfirm PS5-REMOTE-PLAY.spec
```

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

A simple dark-themed GUI will open. You can:

- Paste and validate a base64 PSN Account ID
- Choose resolution / FPS / decode mode / codec
- Start the streaming pipeline in demo mode (listens for packets)

## Getting Your Base64 Account ID

```bash
python tools/get_account_id.py
```

## Project Structure

```
PS5-REMOTE-PLAY/
├── main.py                 # GUI entry point (becomes the .exe)
├── build.bat               # One-click Windows builder
├── PS5-REMOTE-PLAY.spec    # PyInstaller configuration
├── requirements.txt
├── src/
│   ├── core/
│   │   └── account.py
│   └── stream/
│       ├── config.py
│       ├── receiver.py
│       ├── crypto.py
│       ├── decoder.py
│       └── pipeline.py
├── tools/
│   └── get_account_id.py
└── docs/
    └── architecture.md
```

## License

MIT License – see [LICENSE](LICENSE).

## Disclaimer

This project is not affiliated with, endorsed by, or connected to Sony Interactive Entertainment in any way.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.  
This is an independent open-source effort for educational and personal use.

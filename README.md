# PS5-REMOTE-PLAY

**Independent open-source PlayStation Remote Play client** for PS4 and PS5.

This is a **from-scratch** implementation focused on maximum compatibility with older / lower-powered hardware. It is **not** a fork of Chiaki or any other existing project.

## Current Status

| Component                | Status                                      |
|--------------------------|---------------------------------------------|
| Account ID tooling       | Done                                        |
| Discovery                | Implemented (structure + probe)             |
| Registration             | Implemented (Account ID + PIN flow)         |
| Session / control        | Implemented (lifecycle + control channel)   |
| Streaming pipeline       | Implemented (receive → decrypt → decode)    |
| Software decoder         | Working (PyAV / FFmpeg)                     |
| Desktop GUI              | Done – full connect flow                    |
| Windows .exe packaging   | Ready (`build.bat`)                         |
| Exact binary packets     | Still being finalized                       |
| Real console streaming   | Not yet reliable                            |

> The high-level protocol and all public APIs are in place. Exact binary packet formats for discovery/registration/control are the remaining work before reliable real-console connections.

## Build the Windows .exe

1. Install Python 3.10+ on Windows (check “Add to PATH”)
2. Clone or download this repo
3. Double-click **`build.bat`**
4. Get the executable at `dist\PS5-REMOTE-PLAY.exe`

## Running from source

```bash
pip install -r requirements.txt
python main.py
```

## Typical use in the GUI

1. Paste your base64 PSN Account ID → Validate
2. Click **Discover** (or type the console IP)
3. Enter the 8-digit PIN shown on the PlayStation
4. Choose resolution / FPS / decode mode
5. Press **Connect & Start Stream**

## Project Structure

```
PS5-REMOTE-PLAY/
├── main.py                  # GUI
├── build.bat
├── src/
│   ├── core/account.py
│   ├── protocol/            # NEW – discovery, registration, session
│   │   ├── discovery.py
│   │   ├── registration.py
│   │   └── session.py
│   └── stream/              # media pipeline
├── tools/get_account_id.py
└── docs/architecture.md
```

## License

MIT License – see [LICENSE](LICENSE).

## Disclaimer

Not affiliated with Sony Interactive Entertainment.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.

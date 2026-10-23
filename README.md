# PS5-REMOTE-PLAY

**Independent open-source PlayStation Remote Play client** for PS4 and PS5.

This is a **from-scratch** implementation focused on maximum compatibility with older / lower-powered hardware. It is **not** a fork of Chiaki or any other existing project.

## Download the Windows .exe

### Every commit
The Windows `.exe` is **built automatically on every push** to `main`.

1. Go to the **Actions** tab:  
   https://github.com/joeyfrogge-jpg/PS5-REMOTE-PLAY/actions
2. Open the latest successful “Build Windows Release” run
3. Download the artifact **PS5-REMOTE-PLAY-windows** (contains `PS5-REMOTE-PLAY.exe`)

Artifacts are kept for 30 days.

### Official Releases (versioned)
When you create a version tag (`v0.1.0`, `v0.2.0`, …), the same workflow also publishes a proper **GitHub Release** with the `.exe` attached:

**https://github.com/joeyfrogge-jpg/PS5-REMOTE-PLAY/releases**

To make a new Release:
1. Releases → Create a new release
2. Create a tag like `v0.1.0`
3. Publish release → the `.exe` is attached automatically

---

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
| Windows .exe packaging   | Built on every commit + on tags             |
| Exact binary packets     | Still being finalized                       |
| Real console streaming   | Not yet reliable                            |

## Local build (optional)

1. Install Python 3.10+ on Windows
2. Double-click **`build.bat`**
3. Get the executable at `dist\PS5-REMOTE-PLAY.exe`

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
├── main.py
├── build.bat
├── .github/workflows/build-release.yml   # Builds .exe on every commit
├── src/
│   ├── core/
│   ├── protocol/
│   └── stream/
├── tools/
└── docs/
```

## License

MIT License – see [LICENSE](LICENSE).

## Disclaimer

Not affiliated with Sony Interactive Entertainment.  
PlayStation, PS5, PS4, and Remote Play are trademarks of Sony Interactive Entertainment Inc.

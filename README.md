# PS5-REMOTE-PLAY

**Independent open-source PlayStation Remote Play client** for PS4 and PS5.

This is a **from-scratch** implementation focused on maximum compatibility with older / lower-powered hardware. It is **not** a fork of Chiaki or any other existing project.

## Download the Windows .exe (GitHub Releases)

Pre-built executables are published on the **Releases** page:

**https://github.com/joeyfrogge-jpg/PS5-REMOTE-PLAY/releases**

### How to create a new Release (you only need to do this once per version)

1. Go to the repository on GitHub
2. Click **Releases** → **Create a new release**
3. In “Choose a tag”, type a new tag such as `v0.1.0` and click **Create new tag**
4. Title it (e.g. `v0.1.0 – First public build`)
5. Click **Publish release**

The GitHub Actions workflow will automatically:
- Build the Windows `.exe` on a real Windows runner
- Attach `PS5-REMOTE-PLAY.exe` to that release

You can also trigger a build manually from the **Actions** tab → “Build Windows Release” → “Run workflow”.

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
| Windows .exe packaging   | Ready (`build.bat` + GitHub Actions)        |
| Exact binary packets     | Still being finalized                       |
| Real console streaming   | Not yet reliable                            |

## Local build (optional)

If you prefer to build yourself:

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
├── .github/workflows/build-release.yml   # Auto-builds .exe on tag
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

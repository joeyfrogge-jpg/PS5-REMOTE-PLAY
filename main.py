#!/usr/bin/env python3
"""
PS5-REMOTE-PLAY – Main entry point

This is the application launcher. When frozen with PyInstaller it becomes
the .exe entry point.
"""

from __future__ import annotations

import argparse
import logging
import sys
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import queue

# Make sure src is importable both in development and when frozen
if getattr(sys, "frozen", False):
    # Running as compiled .exe
    import os
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    # Running from source
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.account import account_id_to_base64, base64_to_account_id
from src.stream import StreamPipeline, StreamConfig
from src.stream.config import DecodeMode, VideoCodec


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("ps5-remote-play")


class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PS5-REMOTE-PLAY")
        self.geometry("720x560")
        self.minsize(640, 480)

        # Dark-ish theme for a more modern feel
        self.configure(bg="#1e1e1e")
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        style.configure(".", background="#1e1e1e", foreground="#e0e0e0")
        style.configure("TLabel", background="#1e1e1e", foreground="#e0e0e0")
        style.configure("TButton", background="#333333", foreground="#ffffff")
        style.configure("TFrame", background="#1e1e1e")
        style.configure("TLabelframe", background="#1e1e1e", foreground="#e0e0e0")
        style.configure("TLabelframe.Label", background="#1e1e1e", foreground="#ff8c00")
        style.configure("TEntry", fieldbackground="#2d2d2d", foreground="#ffffff")
        style.configure("TCombobox", fieldbackground="#2d2d2d", foreground="#ffffff")

        self.pipeline: StreamPipeline | None = None
        self.log_queue: queue.Queue[str] = queue.Queue()

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        # Header
        header = ttk.Label(
            main,
            text="PS5-REMOTE-PLAY",
            font=("Segoe UI", 18, "bold"),
            foreground="#ff8c00",
        )
        header.pack(pady=(0, 4))

        subtitle = ttk.Label(
            main,
            text="Independent open-source Remote Play client  •  Older hardware focused",
            font=("Segoe UI", 9),
        )
        subtitle.pack(pady=(0, 12))

        # Account ID section
        acct_frame = ttk.LabelFrame(main, text="PSN Account ID (base64)", padding=8)
        acct_frame.pack(fill=tk.X, pady=6)

        self.account_id_var = tk.StringVar()
        ttk.Entry(acct_frame, textvariable=self.account_id_var, width=50).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(acct_frame, text="Validate", command=self._validate_account_id).pack(
            side=tk.LEFT
        )

        # Stream settings
        settings = ttk.LabelFrame(main, text="Stream Settings (older-hardware defaults)", padding=8)
        settings.pack(fill=tk.X, pady=6)

        row1 = ttk.Frame(settings)
        row1.pack(fill=tk.X, pady=2)

        ttk.Label(row1, text="Max Resolution:").pack(side=tk.LEFT)
        self.res_var = tk.StringVar(value="1280x720")
        ttk.Combobox(
            row1,
            textvariable=self.res_var,
            values=["1920x1080", "1280x720", "960x540", "640x360"],
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(row1, text="FPS:").pack(side=tk.LEFT, padx=(16, 0))
        self.fps_var = tk.StringVar(value="30")
        ttk.Combobox(
            row1,
            textvariable=self.fps_var,
            values=["60", "30", "20"],
            width=6,
            state="readonly",
        ).pack(side=tk.LEFT, padx=8)

        row2 = ttk.Frame(settings)
        row2.pack(fill=tk.X, pady=2)

        ttk.Label(row2, text="Decode Mode:").pack(side=tk.LEFT)
        self.decode_var = tk.StringVar(value="software")
        ttk.Combobox(
            row2,
            textvariable=self.decode_var,
            values=["software", "auto", "hardware"],
            width=12,
            state="readonly",
        ).pack(side=tk.LEFT, padx=8)

        ttk.Label(row2, text="Codec:").pack(side=tk.LEFT, padx=(16, 0))
        self.codec_var = tk.StringVar(value="h264")
        ttk.Combobox(
            row2,
            textvariable=self.codec_var,
            values=["h264", "hevc"],
            width=8,
            state="readonly",
        ).pack(side=tk.LEFT, padx=8)

        # Buttons
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill=tk.X, pady=10)

        self.start_btn = ttk.Button(
            btn_frame, text="Start Pipeline (Demo)", command=self._start_pipeline
        )
        self.start_btn.pack(side=tk.LEFT, padx=(0, 8))

        self.stop_btn = ttk.Button(
            btn_frame, text="Stop", command=self._stop_pipeline, state=tk.DISABLED
        )
        self.stop_btn.pack(side=tk.LEFT)

        ttk.Button(btn_frame, text="About", command=self._show_about).pack(side=tk.RIGHT)

        # Log area
        log_frame = ttk.LabelFrame(main, text="Log", padding=4)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=6)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=12,
            bg="#121212",
            fg="#c0c0c0",
            insertbackground="#ffffff",
            font=("Consolas", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        self._log("PS5-REMOTE-PLAY ready.")
        self._log("This is the current skeleton. Full console connection is not yet implemented.")
        self._log("Use the settings above and press ‘Start Pipeline (Demo)’ to exercise the streaming layers.")

    def _log(self, msg: str):
        self.log_queue.put(msg)

    def _poll_log_queue(self):
        try:
            while True:
                msg = self.log_queue.get_nowait()
                self.log_text.configure(state=tk.NORMAL)
                self.log_text.insert(tk.END, msg + "\n")
                self.log_text.see(tk.END)
                self.log_text.configure(state=tk.DISABLED)
        except queue.Empty:
            pass
        self.after(100, self._poll_log_queue)

    def _validate_account_id(self):
        value = self.account_id_var.get().strip()
        if not value:
            messagebox.showwarning("Account ID", "Please paste a base64 Account ID.")
            return
        try:
            numeric = base64_to_account_id(value)
            roundtrip = account_id_to_base64(numeric)
            self._log(f"Account ID valid. Numeric: {numeric}")
            self._log(f"Round-trip base64: {roundtrip}")
            messagebox.showinfo("Account ID", f"Valid!\n\nNumeric ID: {numeric}")
        except Exception as e:
            self._log(f"Invalid Account ID: {e}")
            messagebox.showerror("Account ID", f"Invalid base64 Account ID:\n{e}")

    def _start_pipeline(self):
        if self.pipeline and self.pipeline.is_running:
            return

        try:
            w, h = self.res_var.get().split("x")
            width, height = int(w), int(h)
            fps = int(self.fps_var.get())
            decode = DecodeMode(self.decode_var.get())
            codec = VideoCodec.H264 if self.codec_var.get() == "h264" else VideoCodec.H265

            config = StreamConfig(
                max_width=width,
                max_height=height,
                target_fps=fps,
                decode_mode=decode,
                preferred_codec=codec,
            )

            self.pipeline = StreamPipeline(config)

            def run():
                import asyncio

                async def _run():
                    try:
                        port = await self.pipeline.start()
                        self._log(f"Pipeline started on UDP port {port}")
                        self._log("Waiting for media packets (none will arrive until a real session exists)...")
                        # Keep alive until stopped
                        while self.pipeline and self.pipeline.is_running:
                            await asyncio.sleep(0.5)
                    except Exception as e:
                        self._log(f"Pipeline error: {e}")
                        logger.exception("Pipeline failed")

                asyncio.run(_run())

            threading.Thread(target=run, daemon=True).start()

            self.start_btn.configure(state=tk.DISABLED)
            self.stop_btn.configure(state=tk.NORMAL)
            self._log(
                f"Starting pipeline → {width}x{height}@{fps}fps, "
                f"decode={decode.value}, codec={codec.value}"
            )

        except Exception as e:
            self._log(f"Failed to start: {e}")
            messagebox.showerror("Error", str(e))

    def _stop_pipeline(self):
        if not self.pipeline:
            return

        def stop():
            import asyncio

            async def _stop():
                await self.pipeline.stop()
                self._log("Pipeline stopped.")

            try:
                asyncio.run(_stop())
            except Exception as e:
                self._log(f"Stop error: {e}")

            self.pipeline = None
            self.start_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)

        threading.Thread(target=stop, daemon=True).start()

    def _show_about(self):
        messagebox.showinfo(
            "About PS5-REMOTE-PLAY",
            "PS5-REMOTE-PLAY\n\n"
            "Independent open-source PlayStation Remote Play client\n"
            "focused on older / lower-powered hardware.\n\n"
            "This is currently a development skeleton.\n"
            "Full console connection is not yet implemented.\n\n"
            "Not affiliated with Sony or Chiaki.",
        )


def main():
    parser = argparse.ArgumentParser(description="PS5-REMOTE-PLAY")
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in simple CLI mode instead of GUI",
    )
    args = parser.parse_args()

    if args.cli:
        print("PS5-REMOTE-PLAY – CLI mode")
        print("Full interactive CLI is not implemented yet. Launch without --cli for the GUI.")
        return

    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()

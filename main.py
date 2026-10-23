#!/usr/bin/env python3
"""
PS5-REMOTE-PLAY – Main entry point

GUI launcher that uses the independent protocol + streaming layers.
When frozen with PyInstaller this becomes the .exe.
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import sys
import threading
import queue
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext

if getattr(sys, "frozen", False):
    import os
    sys.path.insert(0, os.path.dirname(sys.executable))
else:
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.core.account import account_id_to_base64, base64_to_account_id
from src.stream import StreamConfig
from src.stream.config import DecodeMode, VideoCodec
from src.protocol import (
    ConsoleInfo,
    discover_consoles,
    RemotePlaySession,
    SessionState,
)

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
        self.geometry("780x640")
        self.minsize(700, 520)

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

        self.session: RemotePlaySession | None = None
        self.discovered: list[ConsoleInfo] = []
        self.log_queue: queue.Queue[str] = queue.Queue()

        self._build_ui()
        self._poll_log_queue()

    def _build_ui(self):
        main = ttk.Frame(self, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        ttk.Label(
            main, text="PS5-REMOTE-PLAY",
            font=("Segoe UI", 18, "bold"), foreground="#ff8c00",
        ).pack(pady=(0, 2))

        ttk.Label(
            main,
            text="Independent open-source client  •  Older hardware focused  •  Not Chiaki",
            font=("Segoe UI", 9),
        ).pack(pady=(0, 10))

        # Account ID
        acct = ttk.LabelFrame(main, text="PSN Account ID (base64)", padding=8)
        acct.pack(fill=tk.X, pady=4)
        self.account_id_var = tk.StringVar()
        ttk.Entry(acct, textvariable=self.account_id_var).pack(
            side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8)
        )
        ttk.Button(acct, text="Validate", command=self._validate_account_id).pack(side=tk.LEFT)

        # Console connection
        conn = ttk.LabelFrame(main, text="Console", padding=8)
        conn.pack(fill=tk.X, pady=4)

        row = ttk.Frame(conn)
        row.pack(fill=tk.X, pady=2)
        ttk.Label(row, text="Host IP:").pack(side=tk.LEFT)
        self.host_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.host_var, width=18).pack(side=tk.LEFT, padx=6)
        ttk.Label(row, text="PIN (8 digits):").pack(side=tk.LEFT, padx=(12, 0))
        self.pin_var = tk.StringVar()
        ttk.Entry(row, textvariable=self.pin_var, width=10).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Discover", command=self._discover).pack(side=tk.LEFT, padx=8)

        self.console_list = tk.Listbox(
            conn, height=3, bg="#121212", fg="#e0e0e0",
            selectbackground="#ff8c00", selectforeground="#000000",
            font=("Consolas", 9),
        )
        self.console_list.pack(fill=tk.X, pady=4)
        self.console_list.bind("<<ListboxSelect>>", self._on_console_select)

        # Stream settings
        settings = ttk.LabelFrame(main, text="Stream Settings", padding=8)
        settings.pack(fill=tk.X, pady=4)

        r1 = ttk.Frame(settings)
        r1.pack(fill=tk.X, pady=2)
        ttk.Label(r1, text="Resolution:").pack(side=tk.LEFT)
        self.res_var = tk.StringVar(value="1280x720")
        ttk.Combobox(
            r1, textvariable=self.res_var,
            values=["1920x1080", "1280x720", "960x540", "640x360"],
            width=12, state="readonly",
        ).pack(side=tk.LEFT, padx=6)

        ttk.Label(r1, text="FPS:").pack(side=tk.LEFT, padx=(12, 0))
        self.fps_var = tk.StringVar(value="30")
        ttk.Combobox(
            r1, textvariable=self.fps_var, values=["60", "30", "20"],
            width=5, state="readonly",
        ).pack(side=tk.LEFT, padx=6)

        ttk.Label(r1, text="Decode:").pack(side=tk.LEFT, padx=(12, 0))
        self.decode_var = tk.StringVar(value="software")
        ttk.Combobox(
            r1, textvariable=self.decode_var,
            values=["software", "auto", "hardware"], width=10, state="readonly",
        ).pack(side=tk.LEFT, padx=6)

        ttk.Label(r1, text="Codec:").pack(side=tk.LEFT, padx=(12, 0))
        self.codec_var = tk.StringVar(value="h264")
        ttk.Combobox(
            r1, textvariable=self.codec_var, values=["h264", "hevc"],
            width=7, state="readonly",
        ).pack(side=tk.LEFT, padx=6)

        # Action buttons
        btns = ttk.Frame(main)
        btns.pack(fill=tk.X, pady=8)
        self.connect_btn = ttk.Button(btns, text="Connect & Start Stream", command=self._connect)
        self.connect_btn.pack(side=tk.LEFT, padx=(0, 8))
        self.stop_btn = ttk.Button(btns, text="Stop", command=self._stop, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT)
        ttk.Button(btns, text="About", command=self._about).pack(side=tk.RIGHT)

        # Log
        logf = ttk.LabelFrame(main, text="Log", padding=4)
        logf.pack(fill=tk.BOTH, expand=True, pady=4)
        self.log_text = scrolledtext.ScrolledText(
            logf, height=12, bg="#121212", fg="#c0c0c0",
            insertbackground="#ffffff", font=("Consolas", 9),
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.configure(state=tk.DISABLED)

        self._log("PS5-REMOTE-PLAY ready.")
        self._log("1. Paste your base64 Account ID and click Validate.")
        self._log("2. Click Discover (or type the console IP manually).")
        self._log("3. Enter the 8-digit PIN shown on your PlayStation and press Connect.")
        self._log("Note: Full binary protocol is still being completed – connection may not succeed yet.")

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
        self.after(120, self._poll_log_queue)

    def _validate_account_id(self):
        value = self.account_id_var.get().strip()
        if not value:
            messagebox.showwarning("Account ID", "Paste a base64 Account ID first.")
            return
        try:
            numeric = base64_to_account_id(value)
            self._log(f"Account ID valid → numeric {numeric}")
            messagebox.showinfo("Account ID", f"Valid.\n\nNumeric: {numeric}")
        except Exception as e:
            self._log(f"Invalid Account ID: {e}")
            messagebox.showerror("Account ID", str(e))

    def _discover(self):
        self._log("Discovering consoles on the local network...")

        def work():
            try:
                consoles = asyncio.run(discover_consoles(timeout=3.0))
                self.discovered = consoles
                self.console_list.delete(0, tk.END)
                if not consoles:
                    self._log("No consoles responded. You can still type the IP manually.")
                for c in consoles:
                    self.console_list.insert(tk.END, str(c))
                    self._log(f"Found: {c}")
            except Exception as e:
                self._log(f"Discovery error: {e}")

        threading.Thread(target=work, daemon=True).start()

    def _on_console_select(self, _event=None):
        sel = self.console_list.curselection()
        if sel and self.discovered:
            c = self.discovered[sel[0]]
            self.host_var.set(c.host)

    def _make_config(self) -> StreamConfig:
        w, h = self.res_var.get().split("x")
        return StreamConfig(
            max_width=int(w),
            max_height=int(h),
            target_fps=int(self.fps_var.get()),
            decode_mode=DecodeMode(self.decode_var.get()),
            preferred_codec=VideoCodec.H264 if self.codec_var.get() == "h264" else VideoCodec.H265,
        )

    def _connect(self):
        account = self.account_id_var.get().strip()
        host = self.host_var.get().strip()
        pin = self.pin_var.get().strip()

        if not account:
            messagebox.showwarning("Missing", "Account ID is required.")
            return
        if not host:
            messagebox.showwarning("Missing", "Console IP address is required.")
            return
        if not (pin.isdigit() and len(pin) == 8):
            messagebox.showwarning("PIN", "PIN must be exactly 8 digits.")
            return

        try:
            base64_to_account_id(account)
        except Exception as e:
            messagebox.showerror("Account ID", f"Invalid: {e}")
            return

        self.connect_btn.configure(state=tk.DISABLED)
        self.stop_btn.configure(state=tk.NORMAL)
        self._log(f"Connecting to {host} with PIN {pin}...")

        def work():
            try:
                config = self._make_config()
                session = RemotePlaySession(account_id_b64=account, stream_config=config)

                # Build a ConsoleInfo for manual entry
                console = ConsoleInfo(name="Manual", host=host, port=9295)
                # Prefer discovered info if available
                for c in self.discovered:
                    if c.host == host:
                        console = c
                        break

                ok = asyncio.run(session.connect(console, pin))
                self.session = session

                if ok:
                    self._log("Session started (STREAMING state).")
                    self._log("Media pipeline is listening. Full binary protocol still being finalized.")
                else:
                    self._log(f"Connect failed: {session.last_error}")
                    self.connect_btn.configure(state=tk.NORMAL)
                    self.stop_btn.configure(state=tk.DISABLED)
                    self.session = None

            except Exception as e:
                self._log(f"Connect error: {e}")
                logger.exception("Connect failed")
                self.connect_btn.configure(state=tk.NORMAL)
                self.stop_btn.configure(state=tk.DISABLED)

        threading.Thread(target=work, daemon=True).start()

    def _stop(self):
        if not self.session:
            return

        def work():
            try:
                asyncio.run(self.session.stop())
                self._log("Session stopped.")
            except Exception as e:
                self._log(f"Stop error: {e}")
            self.session = None
            self.connect_btn.configure(state=tk.NORMAL)
            self.stop_btn.configure(state=tk.DISABLED)

        threading.Thread(target=work, daemon=True).start()

    def _about(self):
        messagebox.showinfo(
            "About",
            "PS5-REMOTE-PLAY\n\n"
            "Independent open-source PlayStation Remote Play client\n"
            "with focus on older / lower-powered hardware.\n\n"
            "Protocol layer (discovery, registration, session) is present.\n"
            "Exact binary packet formats are still being completed.\n\n"
            "Not affiliated with Sony or Chiaki.",
        )


def main():
    parser = argparse.ArgumentParser(description="PS5-REMOTE-PLAY")
    parser.add_argument("--cli", action="store_true", help="CLI mode (minimal)")
    args = parser.parse_args()

    if args.cli:
        print("PS5-REMOTE-PLAY – use the GUI for full functionality.")
        return

    App().mainloop()


if __name__ == "__main__":
    main()

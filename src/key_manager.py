"""
Stealth-C2 — Key Manager
Handles AES-256 key generation, persistent storage, and rotation.
Key file: ~/.stealth_c2/key.bin (chmod 600, never committed to VCS)
"""

from __future__ import annotations

import os
import stat
import shutil
import secrets
from datetime import datetime, timezone

KEY_DIR  = os.path.expanduser("~/.stealth_c2")
KEY_FILE = os.path.join(KEY_DIR, "key.bin")
KEY_SIZE = 32  # AES-256


def _write_key(key: bytes, path: str) -> None:
    os.makedirs(KEY_DIR, exist_ok=True)
    os.chmod(KEY_DIR, stat.S_IRWXU)
    with open(path, "wb") as fh:
        fh.write(key)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # 0600 — owner only


def generate_key() -> bytes:
    return secrets.token_bytes(KEY_SIZE)


def save_key(key: bytes, path: str = KEY_FILE) -> None:
    _write_key(key, path)


def load_key(path: str = KEY_FILE) -> bytes:
    """Load the active key, auto-generating one on first run."""
    if not os.path.exists(path):
        print(f"[key_manager] First run — generating new AES-256 key → {path}")
        key = generate_key()
        save_key(key, path)
        return key

    with open(path, "rb") as fh:
        key = fh.read()

    if len(key) != KEY_SIZE:
        raise ValueError(
            f"[key_manager] Bad key length at '{path}' ({len(key)} bytes). "
            "Delete the file and restart to regenerate."
        )
    return key


def rotate_key(path: str = KEY_FILE) -> bytes:
    """Back up the current key and replace it with a new one."""
    if os.path.exists(path):
        ts          = datetime.now(tz=timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        backup_path = os.path.join(KEY_DIR, f"key_{ts}.bin.bak")
        shutil.copy2(path, backup_path)
        os.chmod(backup_path, stat.S_IRUSR | stat.S_IWUSR)
        print(f"[key_manager] Old key archived → {backup_path}")

    new_key = generate_key()
    save_key(new_key, path)
    print(f"[key_manager] Key rotation complete → {path}")
    return new_key


def list_backups() -> list[str]:
    if not os.path.exists(KEY_DIR):
        return []
    return sorted(
        os.path.join(KEY_DIR, f)
        for f in os.listdir(KEY_DIR)
        if f.endswith(".bin.bak")
    )

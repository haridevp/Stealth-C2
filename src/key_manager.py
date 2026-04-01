"""
key_manager.py — Stealth-C2 V1.0 Key Management
=================================================
Handles AES-256 key lifecycle:
  - Auto-generates a cryptographically random key on first run.
  - Persists the key to a hidden directory outside the repo (chmod 600).
  - Supports key rotation with automatic timestamped backups.

Key file location: ~/.stealth_c2/key.bin
Backup location:   ~/.stealth_c2/key_<timestamp>.bin.bak
"""

import os
import stat
import shutil
import secrets
from datetime import datetime

# --- CONFIGURATION ---

KEY_DIR  = os.path.expanduser("~/.stealth_c2")
KEY_FILE = os.path.join(KEY_DIR, "key.bin")
KEY_SIZE = 32  # 256-bit AES key


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _ensure_key_dir() -> None:
    """Create the hidden key directory if it doesn't already exist."""
    os.makedirs(KEY_DIR, exist_ok=True)
    # Restrict the directory to the owner only
    os.chmod(KEY_DIR, stat.S_IRWXU)


def _write_key(key: bytes, path: str) -> None:
    """Write raw key bytes to *path*, then lock permissions to 0600."""
    _ensure_key_dir()
    with open(path, "wb") as f:
        f.write(key)
    os.chmod(path, stat.S_IRUSR | stat.S_IWUSR)  # -rw-------


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_key() -> bytes:
    """Return a new cryptographically random 32-byte AES-256 key."""
    return secrets.token_bytes(KEY_SIZE)


def save_key(key: bytes, path: str = KEY_FILE) -> None:
    """
    Persist *key* to *path*.

    The file and its parent directory are created automatically.
    Permissions are locked to 0600 (owner read/write only).
    """
    _write_key(key, path)


def load_key(path: str = KEY_FILE) -> bytes:
    """
    Load and return the AES key from *path*.

    If the file doesn't exist this is treated as a first run:
    a new key is generated, saved, and returned.

    Raises:
        ValueError: If the stored key is not exactly KEY_SIZE bytes.
    """
    if not os.path.exists(path):
        print(f"[*] Key Manager: No key found at {path}. Bootstrapping new key...")
        key = generate_key()
        save_key(key, path)
        print(f"[*] Key Manager: New AES-256 key saved to {path}")
        return key

    with open(path, "rb") as f:
        key = f.read()

    if len(key) != KEY_SIZE:
        raise ValueError(
            f"[!] Key Manager: Key at {path} is {len(key)} bytes — expected {KEY_SIZE}. "
            "Delete the file and restart to auto-generate a valid key."
        )

    return key


def rotate_key(path: str = KEY_FILE) -> bytes:
    """
    Generate a new AES-256 key, back up the current one, and save the new one.

    The backup is stored in KEY_DIR as ``key_<ISO-timestamp>.bin.bak``.

    Returns:
        bytes: The newly generated key.
    """
    # 1. Back up the existing key (if any)
    if os.path.exists(path):
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        backup_path = os.path.join(KEY_DIR, f"key_{timestamp}.bin.bak")
        shutil.copy2(path, backup_path)
        os.chmod(backup_path, stat.S_IRUSR | stat.S_IWUSR)
        print(f"[*] Key Manager: Old key backed up → {backup_path}")

    # 2. Generate and persist the new key
    new_key = generate_key()
    save_key(new_key, path)
    print(f"[*] Key Manager: Key rotated. New key saved to {path}")

    return new_key


def list_backups() -> list[str]:
    """Return a sorted list of backup key file paths in KEY_DIR."""
    if not os.path.exists(KEY_DIR):
        return []
    return sorted(
        os.path.join(KEY_DIR, f)
        for f in os.listdir(KEY_DIR)
        if f.endswith(".bin.bak")
    )

"""
Stealth-C2 — Configuration
Central constants. AES key is loaded from disk, never hardcoded.
"""

from __future__ import annotations

import os
import key_manager

# Loaded from ~/.stealth_c2/key.bin on startup (auto-generated on first run).
AES_KEY: bytes = key_manager.load_key()

TEMP_DIR: str = os.path.join(os.getcwd(), "temp_data")
os.makedirs(TEMP_DIR, exist_ok=True)
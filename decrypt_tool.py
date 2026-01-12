import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

# MUST MATCH THE KEY IN src/config.py
AES_KEY = b'this_is_a_secret_32_byte_key_!!!'

def decrypt_file(enc_filepath):
    try:
        with open(enc_filepath, 'rb') as f:
            file_data = f.read()
            
        # Extract Nonce (First 12 bytes) and Ciphertext (The rest)
        nonce = file_data[:12]
        ciphertext = file_data[12:]
        
        aesgcm = AESGCM(AES_KEY)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        
        # Save decrypted file (remove .enc)
        out_path = enc_filepath.replace(".enc", "")
        with open(out_path, 'wb') as f:
            f.write(plaintext)
            
        print(f"✅ Decrypted: {out_path}")
        
    except Exception as e:
        print(f"❌ Decryption Failed: {e}")

if __name__ == "__main__":
    path = input("Enter path to .enc file: ").strip().strip('"') # Clean quotes
    decrypt_file(path)
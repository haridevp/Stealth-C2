import sys
import os

# List of common analysis tool process names (simplified for portfolio)
BLACKLISTED_PROCESSES = [
    "wireshark", "fiddler", "processhacker", "x64dbg"
]

def check_sandbox():
    """
    Simple check to see if we are running in a hostile environment.
    """
    # 1. Check for common sandbox environment variables
    if os.environ.get("CUCKOO_ANALYSIS_TASK_ID"):
        return True
    
    # 2. (Optional) Check simple mouse movement or uptime in a real malware
    # For this portfolio, we will return False (Safe) so it works on your PC.
    return False

def kill_switch():
    """
    Terminates the program immediately if a threat is detected.
    """
    print("⚠️ THREAT DETECTED: Kill Switch Engaged.")
    sys.exit(0)
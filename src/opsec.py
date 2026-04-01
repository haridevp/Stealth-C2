"""
Stealth-C2 — OpSec Module
Pre-flight checks that run before the agent connects.
Kills the process if analysis tools or sandbox indicators are detected.
"""

from __future__ import annotations

import os
import sys
import subprocess
import platform
import time

# Processes that indicate an active analysis environment
BLACKLISTED_PROCESSES: list[str] = [
    "wireshark", "fiddler", "tcpview", "processhacker",
    "procmon", "ida64", "ida", "x64dbg", "x32dbg", "ollydbg",
]

# Environment variable name substrings common in sandbox platforms
SANDBOX_ENV_MARKERS: list[str] = [
    "CUCKOO", "VBOX", "VMWARE", "SANDBOXIE", "ANALYSIS",
]


def check_process_list() -> bool:
    system = platform.system()
    try:
        if system == "Windows":
            output = subprocess.check_output("tasklist", shell=True).decode().lower()
        elif system == "Linux":
            output = subprocess.check_output(["ps", "-A"], text=True).lower()
        else:
            return False
        for proc in BLACKLISTED_PROCESSES:
            if proc in output:
                print(f"[opsec] Threat detected — '{proc}' is running.")
                return True
    except Exception as e:
        print(f"[opsec] Process scan error: {e}")
    return False


def check_sandbox_env() -> bool:
    for var in os.environ:
        for marker in SANDBOX_ENV_MARKERS:
            if marker in var.upper():
                print(f"[opsec] Sandbox indicator found: {var}")
                return True
    return False


def is_compromised() -> bool:
    return check_sandbox_env() or check_process_list()


def engage_kill_switch() -> None:
    print("[opsec] ⛔  Threat detected — terminating to protect OpSec.")
    time.sleep(1)
    sys.exit(0)
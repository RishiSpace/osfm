import socket
import subprocess
import os
import sys
from win10toast import ToastNotifier
from plyer import notification
import threading

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

def show_toast_notification(title, message):  # Updated to accept title and message
    threading.Thread(notification.notify(
        title=title,
        message=message,
        app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
        timeout=10,  # seconds
    ))

def fix_windows():
    try:
            print("Running System File Checker (sfc)...")
            sfc_result = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True)
            if sfc_result.returncode == 0:
                print("sfc completed successfully.")
                print(sfc_result.stdout)
            else:
                print("sfc encountered an error.")
                print(sfc_result.stderr)


            print("Running DISM to check the health of the Windows image...")
            dism_check = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"], capture_output=True, text=True)
            print(dism_check.stdout)
            print("Running DISM to scan the Windows image for corruption...")
            dism_scan = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/ScanHealth"], capture_output=True, text=True)
            print(dism_scan.stdout)
            print("Running DISM to repair the Windows image...")
            dism_repair = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"], capture_output=True, text=True)
            print(dism_repair.stdout)
            print("Windows fix process completed.")

    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e.stderr}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
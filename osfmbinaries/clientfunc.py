import subprocess
import socket
import os
import threading

from osfmbinaries.utils import show_toast_notification

def uninstall_software(software_id):  # Redundant, but kept if you need local uninstall logic outside server class
    try:
        print(f"Uninstalling software with ID: {software_id}")
        uninst = (f"winget uninstall {software_id}")
        result = subprocess.run(uninst, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"Uninstall succeeded: {result.stdout}")
        else:
            print(f"Uninstall failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Uninstall command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while uninstalling software: {e}")


def execute_command(command): # Redundant, may be useful later
    try:
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Command succeeded: {result.stdout}")
        else:
            print(f"Command failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while executing command: {e}")


# Get the current network category (Private/Public)
def get_network_category():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetConnectionProfile | Select-Object -ExpandProperty NetworkCategory"],
            capture_output=True, text=True, check=True
        )
        network_category = result.stdout.strip()
        print(f"Current network category: {network_category}")
        return network_category
    except subprocess.CalledProcessError as e:
        print(f"Error getting network category: {e}")
        return None

# Change the network profile to Private
def change_network_to_private():
    try:
        print("Attempting to change network profile to Private...")
        command = (
            "Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -eq 'Public'} | "
            "Set-NetConnectionProfile -NetworkCategory Private"
        )
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        print(f"Network profile changed to Private. Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing network profile: {e}")
        print(f"Error output: {e.stderr}")
        return False

# Check if Remote Desktop Protocol (RDP) is enabled
def check_rdp_status():
    try:
        command = r"Get-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' | Select-Object -ExpandProperty fDenyTSConnections"
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        rdp_status = int(result.stdout.strip())
        if rdp_status == 0:
            print("RDP is enabled.")
        else:
            print("RDP is disabled.")
        return rdp_status == 0
    except subprocess.CalledProcessError as e:
        print(f"Error checking RDP status: {e}")
        print(f"Error output: {e.stderr}")
        return None

# Enable RDP and set the network profile to Private if necessary
def enable_rdp():
    print("Checking network profile and RDP status...")

    # Check current network profile
    current_profile = get_network_category()
    if current_profile != "Private":
        print(f"Current network profile is '{current_profile}'. Changing to Private...")
        if not change_network_to_private():
            print("Failed to change network profile to Private. RDP may not be enabled correctly.")
            return False
    else:
        print("Network profile is already set to Private.")

    # Check if RDP is already enabled
    rdp_status = check_rdp_status()
    if rdp_status is True:
        print("RDP is already enabled.")
        return True
    elif rdp_status is None:
        print("Unable to determine RDP status. Proceeding with enable process.")
    else:
        print("RDP is currently disabled. Enabling RDP...")

    # Commands to enable RDP
    commands = [
        ("Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'", "Error enabling firewall rules"),
        (r"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0", "Error setting RDP properties"),
        ("Restart-Service -Name 'TermService' -Force", "Error restarting RDP service")
    ]

    try:
        for command, error_message in commands:
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
            print(f"Successfully executed: {command}")
            print(f"Output: {result.stdout}")

        # Verify RDP is enabled after the process
        if check_rdp_status():
            print("RDP enabled successfully.")
            return True
        else:
            print("RDP enabling process completed, but final status check failed.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Exception occurred while enabling RDP: {e}")
        return False

# Discover server on the network via UDP broadcast
def discover_server(port=12345):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(5)

    try:
        udp_socket.sendto(b"DISCOVER_SERVER", ('<broadcast>', port))
        print("Broadcasted discovery message.")
        try:
            response, addr = udp_socket.recvfrom(1024)
            if response == b"SERVER_HERE":
                return addr[0]
        except socket.timeout:
            print("No server response received.")
    except socket.error as e:
        print(f"UDP socket error: {e}")
    finally:
        udp_socket.close()

    return None

# Connect to the discovered server
def connect_to_server(server_ip, port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, port))
        hostname = socket.gethostname()
        print(f"Sending hostname: {hostname}")
        client_socket.sendall(f"HOSTNAME {hostname}".encode())
        # Show the toast notification here
        show_toast_notification("OSFM-Control", "This system is currently being controlled by an Administrator")
        return client_socket
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to server: {e}")
        client_socket.close()
        return None
    
def install_pro(file_path):
    subprocess.run(f"cmd.exe /c {file_path}")

def install_software(file_path):
        if os.path.isdir(file_path):
            files = os.listdir(file_path)
            executables = [f for f in files if f.endswith(('.exe', '.msi'))]
            if not executables:
                print("No executable files found in the directory.")
                return
            for executable in executables:
                full_path = os.path.join(file_path, executable)
                print(f"Installing {full_path}...")
                # Use Start-Process to execute the installer with the UNC path
                command = f'cmd.exe /c "{full_path}" /quiet'
                print(command)
                subprocess.run(command)
        else:
            print(f"The path is not a directory: {file_path}")

def download_and_install_software(server_ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((server_ip, port))
            tcp_socket.sendall(b"UPLOAD")
            file_name = tcp_socket.recv(1024).decode()
            file_path = os.path.join(os.path.expanduser("~"), file_name)
            with open(file_path, "wb") as f:
                while True:
                    data = tcp_socket.recv(4096)
                    if data == b"END_OF_FILE":
                        break
                    f.write(data)
            print(f"File downloaded and saved to {file_path}")
            install_software(file_path)
    except Exception as e:
        print(f"Error downloading and installing software: {e}")
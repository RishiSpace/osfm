import subprocess
import socket
import time
import os
import subprocess

def uninstall_software(software_id):
    try:
        print(f"Uninstalling software with ID: {software_id}")
        result = subprocess.run(["winget", "uninstall", "--id", software_id], capture_output=True, text=True, check=True)
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

def execute_command(command):
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

def enable_rdp():
    commands = [
        ("Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'", "Error enabling firewall rules"),
        ("Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0", "Error setting RDP properties"),
        ("Restart-Service -Name 'TermService'", "Error restarting RDP service")
    ]
    try:
        print("Enabling RDP...")
        for command, error_message in commands:
            subprocess.run(["powershell", "-Command", command], check=True)
            print(f"Successfully executed: {command}")
        print("RDP enabled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Exception occurred while enabling RDP: {e}")

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

def connect_to_server(server_ip, port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.settimeout(10)
    try:
        client_socket.connect((server_ip, port))
        hostname = socket.gethostname()
        print(f"Sending hostname: {hostname}")
        client_socket.sendall(f"HOSTNAME {hostname}".encode())
        return client_socket
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to server: {e}")
        client_socket.close()
        return None
    
def handle_file_path(file_path):
    print(f"Handling file path: {file_path}")
    # Additional processing if needed

def install_software(file_path):
    try:
        print(f"Installing software from path: {file_path}")
        result = subprocess.run(["winget", "install", file_path], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"Installation succeeded: {result.stdout}")
        else:
            print(f"Installation failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Installation command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while installing software: {e}")

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

def main():
    port = 12345
    client_socket = None
    file_path = ""  # Initialize file_path variable

    enable_rdp()

    while True:
        if client_socket is None:
            print("Searching for server...")
            server_ip = discover_server(port)
            if server_ip:
                print(f"Found server at {server_ip}.")
                client_socket = connect_to_server(server_ip, port)
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)
        else:
            try:
                client_socket.settimeout(None)  # No timeout for receive operations
                data = client_socket.recv(1024)
                if not data:
                    raise ConnectionResetError("Server disconnected")

                command = data.decode()
                print(f"Received command: {command}")

                if command.startswith("FILE_PATH"):
                    file_path = command[len("FILE_PATH "):].strip()
                    handle_file_path(file_path)
                elif command == "INSTALL":
                    if file_path:  # Ensure file_path is set
                        print(f"Attempting to install software: {file_path}")
                        install_software(file_path)
                    else:
                        print("No file path specified for INSTALL command.")
                elif command.startswith("POWERSHELL "):
                    ps_command = command[len("POWERSHELL "):]
                    execute_command(f'powershell -Command "{ps_command}"')
                elif command == "UPLOAD":
                    download_and_install_software(client_socket.getpeername()[0], port)
                elif command.startswith("UNINSTALL "):
                    _, software_id = command.split(maxsplit=1)
                    uninstall_software(software_id)
                elif command == "FIX_WINDOWS":
                    execute_command("sfc /scannow")
            except (socket.error, ConnectionResetError) as e:
                print(f"Connection issue: {e}")
                client_socket.close()
                client_socket = None
                print("Reconnecting in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    main()

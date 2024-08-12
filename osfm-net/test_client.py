import socket
import subprocess
import time
import os

# Software Version
Software_Version = "V1.03 (Net)"

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

def execute_command(command):
    try:
        print(f"Executing: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"Command succeeded: {result.stdout}")
        else:
            print(f"Command failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while executing command: {e}")

def enable_rdp():
    commands = [
        """powershell -Command "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0; Enable-NetFirewallRule -DisplayGroup 'Remote Desktop';" """,
        """powershell -Command "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'UserAuthentication' -Value 0;" """,
        """powershell -Command "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services' -Name 'fAllowUnrestrictedRDP' -Value 1;" """
    ]
    for command in commands:
        execute_command(f'powershell -Command "{command}"')

def install_software(file_path):
    # Ensure the file path exists before attempting to change directory
    if os.path.exists(file_path):
        # If the file is an .exe, execute it directly
        if file_path.lower().endswith(".exe"):
            execute_command(f'cd /d {os.path.dirname(file_path)} && ./{os.path.basename(file_path)}')
        else:
            print(f"Unsupported file type for installation: {file_path}")
    else:
        print(f"The file path does not exist: {file_path}")

def handle_file_path(file_path):
    print(f"Formatted file path: {file_path}")
    
    if os.path.exists(file_path):
        print(f"File exists: {file_path}")
        install_software(file_path)
    else:
        print(f"The path does not exist: {file_path}")

def download_and_install_software(server_ip, port):
    client_socket = connect_to_server(server_ip, port)
    if not client_socket:
        return

    try:
        client_socket.sendall(b"UPLOAD_REQUEST")
        network_share_path = client_socket.recv(1024).decode()
        
        print(f"Network share path received: {network_share_path}")

        if os.path.exists(network_share_path):
            install_software(network_share_path)
        else:
            print(f"Network path does not exist: {network_share_path}")

    finally:
        client_socket.close()

def install_python_package(package_path):
    if os.path.isfile(package_path):
        execute_command(f"pip install {package_path}")
    else:
        print(f"Package file does not exist: {package_path}")

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
                elif command.startswith("PIP_INSTALL "):
                    package_name = command[len("PIP_INSTALL "):].strip()
                    package_path = os.path.join(network_share_path, package_name)  # Assuming package_path is known
                    print(f"Attempting to install Python package: {package_path}")
                    install_python_package(package_path)
                elif command == "UPLOAD":
                    download_and_install_software(client_socket.getpeername()[0], port)
                elif command == "UNINSTALL":
                    execute_command("winget uninstall SomeSoftware")
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

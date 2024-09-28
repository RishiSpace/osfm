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
    command = "powershell " + command 
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
        """-Command "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0; Enable-NetFirewallRule -DisplayGroup 'Remote Desktop';" """,
        """-Command "Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'UserAuthentication' -Value 0;" """,
        """-Command "Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services' -Name 'fAllowUnrestrictedRDP' -Value 1;" """
    ]
    
    # Check if RDP is enabled before running commands
    rdp_enabled_check = """-Command "Get-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections'" """
    try:
        result = subprocess.run("powershell " + rdp_enabled_check, shell=True, capture_output=True, text=True)
        if result.returncode == 0 and '1' in result.stdout:
            print("RDP is disabled, enabling...")
            for command in commands:
                execute_command(f'powershell {command}')
        else:
            print("RDP is already enabled.")
    except Exception as e:
        print(f"Failed to check RDP status: {e}")

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

def handle_file_path(file_path):
    print(f"Formatted file path: {file_path}")
    
    # Verify the path exists
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
        
        # Debugging: Print the network share path
        print(f"Network share path received: {network_share_path}")

        # Directly use the network path
        if os.path.exists(network_share_path):
            install_software(network_share_path)
        else:
            print(f"Network path does not exist: {network_share_path}")

    finally:
        client_socket.close()

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

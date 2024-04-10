import socket
import subprocess
from threading import Thread

def handle_command(command_data):
    parts = command_data.split(':', 1)
    command = parts[0]
    if command == 'install' and len(parts) > 1:
        software_ids = parts[1].split(',')
        for software_id in software_ids:
            subprocess.run(["winget", "install", "--id=" + software_id.strip(), "--accept-package-agreements", "--accept-source-agreements"])
    elif command == 'uninstall' and len(parts) > 1:
        software_ids = parts[1].split(',')
        for software_id in software_ids:
            subprocess.run(["winget", "uninstall", "--id=" + software_id.strip()])
    elif command == 'fix':
        subprocess.run(["sfc", "/scannow"])
        subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"])
        subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/ScanHealth"])
        subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"])
    elif command.startswith("powershell:"):
        powershell_command = command.split(":", 1)[1]
        try:
            output = subprocess.check_output(["powershell", "-Command", powershell_command], shell=True)
            client_socket.sendall(output)
        except subprocess.CalledProcessError as e:
            error_msg = str(e).encode('utf-8')
            client_socket.sendall(error_msg)


def listen_for_commands():
    while True:
        try:
            command_data = client_socket.recv(1024).decode('utf-8')
            if command_data:
                handle_command(command_data)
        except Exception as e:
            print(f"Error receiving command: {e}")
            break

def main():
    global client_socket
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = input("Enter the server's IP address: ")
        port = 12345

        client_socket.connect((host, port))
        print("Connected to the server.")

        client_socket.sendall("DISCOVERABLE".encode('utf-8'))

        Thread(target=listen_for_commands).start()

    except Exception as e:
        print(f"Unable to connect to the server: {e}")

if __name__ == "__main__":
    main()

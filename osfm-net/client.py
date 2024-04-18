import socket
import subprocess
import os
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
    elif command.startswith("os:"):
        os_command = command.split(":", 1)[1]
        if os.name == 'nt':  # Check if the OS is Windows
            try:
                output = subprocess.check_output(["powershell", "-Command", os_command], shell=True, stderr=subprocess.STDOUT)
                client_socket.sendall(output)
            except subprocess.CalledProcessError as e:
                error_msg = str(e).encode('utf-8')
                client_socket.sendall(error_msg)
            else:
                try:
                    output = subprocess.check_output(os_command, shell=True, stderr=subprocess.STDOUT)
                    client_socket.sendall(output)
                except subprocess.CalledProcessError as e:
                    error_msg = str(e).encode('utf-8')
                    client_socket.sendall(error_msg)





def listen_for_commands():
    while True:
        try:
            command_data = client_socket.recv(1024).decode('utf-8')
            if command_data:
                print(f"Received command: {command_data}")
                execute_command(command_data)
        except Exception as e:
            print(f"Error receiving command: {e}")
            break

def execute_command(command_data):
    try:
        if command_data.startswith("os:"):
            os_command = command_data.split(":", 1)[1]
            output = subprocess.check_output(["powershell", "-Command", os_command], shell=True, stderr=subprocess.STDOUT)
            print(output.decode('utf-8'))
            client_socket.sendall(output)
        else:
            print("naaaaa")
    except Exception as e:
        print(f"Error executing command: {e}")


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


import socket
import os
import subprocess
from threading import Thread
import shutil
import win32net
import win32netcon

# Function to handle commands from the server
def handle_command(command_data):
    # First, split the command_data to get the command and any additional data
    parts = command_data.split(':', 1)
    command = parts[0]
    if command == 'install' and len(parts) > 1:
        # Extract the software IDs sent by the server
        software_ids = parts[1].split(',')
        for software_id in software_ids:
            # Install each software using winget
            os.system(f"winget install --id={software_id.strip()} --accept-package-agreements --accept-source-agreements")
    elif command == 'uninstall' and len(parts) > 1:
        # Extract the software IDs sent by the server
        software_ids = parts[1].split(',')
        for software_id in software_ids:
            # Uninstall each software using winget
            os.system(f"winget uninstall --id={software_id.strip()}")
    elif command == 'fix':
        # Run Windows repair commands
        os.system("sfc /scannow")
        os.system("DISM /Online /Cleanup-Image /CheckHealth")
        os.system("DISM /Online /Cleanup-Image /ScanHealth")
        os.system("DISM /Online /Cleanup-Image /RestoreHealth")
    elif command == "FILE_TRANSFER_INIT":
        print("Receiving files...")
        receive_and_save_files(client_socket)
    elif command.startswith("FILE:"):
        file_name = command.split(":")[1]
        # Next message will be the file size
        file_size = int(client_socket.recv(1024).decode('utf-8').split(":")[1])
        # Now receive the file content
        with open(file_name, 'wb') as file:
            remaining = file_size
            while remaining:
                content = client_socket.recv(min(1024, remaining))
                file.write(content)
                remaining -= len(content)
        # Copy received file to SMB shared folder
        subprocess.run(["copy", file_name, r"\\{host_ip}\osfm_share".format(host_ip=host)])
    elif command == "FILE_TRANSFER_COMPLETE":
        print("File transfer complete.")

def receive_and_save_files(client_socket):
    while True:
        data = client_socket.recv(1024).decode('utf-8')
        if data == "FILE_TRANSFER_COMPLETE":
            break
        # Implement logic based on the received data
        # This could involve receiving file names, sizes, and then the actual file content

# Function to listen for commands from the server
def listen_for_commands():
    while True:
        try:
            command_data = client_socket.recv(1024).decode('utf-8')
            if command_data:
                # Handle the received command
                handle_command(command_data)
        except Exception as e:
            print(f"Error receiving command: {e}")
            break

# Main function to start the client
def main():
    global client_socket
    try:
        # Create a socket object
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = input("Enter the hostname's IP address: ")
        port = 12345

        # Connect to the server
        client_socket.connect((host, port))
        print("Connected to the server.")

        # Send a message to make this PC discoverable
        client_socket.sendall("DISCOVERABLE".encode('utf-8'))

        # Start listening for commands from the server
        Thread(target=listen_for_commands).start()

        # Check and enable network sharing
        subprocess.run(["net", "share", "osfm_share={path}".format(path=r"C:\Users\Public\Documents\osfm_share"), "/GRANT:Everyone,FULL"])

    except Exception as e:
        print(f"Unable to connect to the server: {e}")

if __name__ == "__main__":
    main()



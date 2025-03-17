import subprocess
import socket
import time
import signal

from osfmbinaries.utils import get_local_hostname, signal_handler, fix_windows, show_toast_notification
from osfmbinaries.clientfunc import discover_server, connect_to_server, install_software

def main_client():
    port = 12345
    client_socket = None
    local_hostname = get_local_hostname()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    while True:
        if client_socket is None:
           if client_socket is None:
            print("Searching for server...")
            server_ip = discover_server(port)
            if server_ip:
                print(f"Found server at {server_ip}.")
                client_socket = connect_to_server(server_ip, port)

                if client_socket:  # Ensure connection was successful
                    try:
                        # Receive the server's hostname from the first message
                        server_hostname = client_socket.recv(1024).decode().split(" ")[0]

                        # Skip connecting if the server hostname is the same as the local hostname
                        if server_hostname == local_hostname:
                            print("Detected server is on the same machine. Skipping connection.")
                            client_socket.close()
                            client_socket = None
                        else:
                            print(f"Connected to server at {server_ip}.")
                            
                    except ConnectionResetError:
                        print("Connection was closed by the server before receiving hostname.")
                        client_socket.close()
                        client_socket = None
                    except Exception as e:
                        print(f"Unexpected error while receiving hostname: {e}")
                        client_socket.close()
                        client_socket = None
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)

        else:
            try:
                response = client_socket.recv(1024).decode()

                if response.startswith("FILE_PATH"):
                    file_path = response.split(" ")[1]
                    if file_path:
                        print(f"Received file path: \{file_path}") #Debugging Info
                        try:
                            install_software(f"\{file_path}")
                            client_socket.sendall("200 OK".encode())
                        except Exception as e:
                            print(f"Error installing software: {e}")
                            client_socket.sendall("500 ERROR".encode())


                    else:
                        print("FILE_PATH received but no valid path provided.") 


                elif response.startswith("POWERSHELL"):
                    ps_command = response.split(" ", 1)[1]
                    try:
                        subprocess.run(["powershell", "-Command", ps_command], check=True)
                        client_socket.sendall("200 OK".encode())
                    except subprocess.CalledProcessError as e:
                        print(f"PowerShell command failed: {e}")
                        client_socket.sendall("500 ERROR".encode())

                elif response.startswith("FIX"):
                    try:
                        fix_windows()
                        client_socket.sendall("200 OK".encode())
                    except Exception as e:
                        print(f"Error fixing windows: {e}")
                        client_socket.sendall("500 ERROR".encode())
                
                elif response.startswith("TOASTC"):
                    user = response.split(" ",1)[1]
                    show_toast_notification("User Management",f"User {user} has been created")
                    client_socket.sendall("200 OK".encode())
                
                elif response.startswith("TOASTD"):
                    user = response.split(" ",1)[1]
                    show_toast_notification("User Management",f"User {user} has been deleted")
                    client_socket.sendall("200 OK".encode())

                elif response == "CLOSE":
                    client_socket.close()
                    client_socket = None
                    print("Server closed the connection. Searching for server again...")

                else:
                    print(f"Received unexpected response: {response}")

            except (ConnectionResetError, socket.error) as e:
                print("Connection to server was forcibly closed. Reconnecting...")
                client_socket.close()
                client_socket = None
            except socket.error as e:
                print(f"Socket error: {e}. Reconnecting...")
                client_socket.close()
                client_socket = None
            except Exception as e:
                print(f"Unexpected error: {e}. Reconnecting...")
                client_socket.close()
                client_socket = None
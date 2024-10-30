import subprocess
import socket
import time
import signal

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
                        server_hostname = client_socket.recv(1024).decode().split(" ")[1]

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
                        print(f"Received file path: {file_path}") #Debugging Info
                        install_software(file_path)


                    else:
                        print("FILE_PATH received but no valid path provided.") 


                elif response.startswith("POWERSHELL"):
                    ps_command = response.split(" ", 1)[1]
                    subprocess.run(["powershell", "-Command", ps_command], check=True)

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
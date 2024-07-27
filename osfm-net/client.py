import socket
import subprocess
import pypsrp
import time
import platform
import getpass

def check_and_enable_rdp():
    # Function to check and enable RDP on the client machine
    try:
        if platform.system() == "Windows":
            username = getpass.getuser()
            password = getpass.getpass(prompt="Enter password for RDP enabling: ")
            
            client = pypsrp.Client("localhost", username, password)

            # Check if RDP is enabled
            rdp_check_command = "Get-Service -Name TermService"
            result = client.execute_ps(rdp_check_command)
            print(f"RDP Status: {result}")

            # Enable RDP if not enabled
            if "Running" not in result:
                enable_rdp_command = """
                Set-Service -Name TermService -StartupType Automatic
                Start-Service -Name TermService
                """
                print("Enabling RDP...")
                client.execute_ps(enable_rdp_command)
                print("RDP Enabled.")
        else:
            print("RDP enabling is only supported on Windows.")
    except Exception as e:
        print(f"Error enabling RDP: {e}")

def main():
    server_ip = "255.255.255.255"  # Broadcast address
    server_port = 12345
    buffer_size = 1024

    while True:
        try:
            # Create a UDP socket for discovering the server
            udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            udp_socket.settimeout(5)
            udp_socket.sendto(b"DISCOVER_SERVER", (server_ip, server_port))

            # Create a TCP socket for connecting to the server
            tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            tcp_socket.settimeout(5)
            tcp_socket.connect((server_ip, server_port))

            print("Connected to server")

            # Start RDP check and enabling if needed
            check_and_enable_rdp()

            while True:
                try:
                    data = tcp_socket.recv(buffer_size)
                    if not data:
                        break
                    print(f"Received: {data.decode()}")
                except socket.timeout:
                    print("Connection timed out, retrying...")
                    break
                except Exception as e:
                    print(f"Connection error: {e}")
                    break

        except socket.timeout:
            print("Server not found, retrying...")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            tcp_socket.close()
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    main()

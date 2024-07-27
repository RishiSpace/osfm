import socket
import customtkinter as CTk
import threading
import subprocess
import platform
import getpass
import pypsrp

class Server:
    def __init__(self, host="0.0.0.0", port=12345):
        self.server_ip = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.connections = {}
        self.setup_ui()
        self.start_udp_listener()  # Start the UDP listener for client discovery
        self.start_tcp_server()  # Start the TCP server
        self.root.mainloop()

    def setup_ui(self):
        self.root = CTk.CTk()
        self.root.geometry("600x400")
        self.root.title("OSFM-Net")  # Updated GUI title

        self.install_button = CTk.CTkButton(self.root, text="Install Software", command=self.install_software)
        self.install_button.pack(pady=10)

        self.uninstall_button = CTk.CTkButton(self.root, text="Uninstall Software", command=self.uninstall_software)
        self.uninstall_button.pack(pady=10)

        self.fix_button = CTk.CTkButton(self.root, text="Fix Windows", command=self.fix_windows)
        self.fix_button.pack(pady=10)

        # Textbox and button for sending PowerShell commands
        self.ps_command_entry = CTk.CTkEntry(self.root, placeholder_text="Enter PowerShell command")
        self.ps_command_entry.pack(pady=10, fill='x')

        self.powershell_button = CTk.CTkButton(self.root, text="Send PowerShell Command", command=self.send_powershell)
        self.powershell_button.pack(pady=10)

        # Frame to list connected clients
        self.clients_frame = CTk.CTkFrame(self.root)
        self.clients_frame.pack(pady=10, fill='both', expand=True)

    def start_udp_listener(self):
        udp_thread = threading.Thread(target=self.udp_listener, daemon=True)
        udp_thread.start()

    def udp_listener(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                udp_socket.bind((self.server_ip, self.server_port))
                print("UDP listener started")
                while True:
                    data, addr = udp_socket.recvfrom(1024)
                    if data == b"DISCOVER_SERVER":
                        udp_socket.sendto(b"SERVER_HERE", addr)
                        print(f"Sent response to {addr}")
        except Exception as e:
            print(f"UDP listener error: {e}")

    def start_tcp_server(self):
        tcp_thread = threading.Thread(target=self.tcp_server, daemon=True)
        tcp_thread.start()

    def tcp_server(self):
        print("TCP server started, waiting for connections...")
        while True:
            try:
                client_socket, address = self.server_socket.accept()
                self.connections[client_socket] = {'address': address, 'hostname': None}
                print(f"Client {address} connected")
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"TCP server error: {e}")

    def handle_client(self, client_socket):
        try:
            hostname = client_socket.recv(1024).decode()
            if hostname:
                self.connections[client_socket]['hostname'] = hostname
                self.update_client_list()
                self.check_and_enable_rdp(client_socket, hostname)
            while True:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
        except Exception as e:
            print(f"Client connection error: {e}")
        finally:
            client_socket.close()
            del self.connections[client_socket]
            self.update_client_list()

    def update_client_list(self):
        for widget in self.clients_frame.winfo_children():
            widget.destroy()

        for conn, info in self.connections.items():
            hostname = info['hostname'] or "Unknown"
            button = CTk.CTkButton(self.clients_frame, text=hostname, command=lambda conn=conn: self.rdp_to_client(conn))
            button.pack(pady=5, fill='x')

    def rdp_to_client(self, conn):
        address = self.connections[conn]['address'][0]
        print(f"Initiating RDP to {address}")
        # For Windows: Use mstsc to initiate RDP connection
        if platform.system() == "Windows":
            subprocess.run(f"mstsc /v:{address}", shell=True)
        else:
            print("RDP not supported on this operating system")

    def check_and_enable_rdp(self, client_socket, hostname):
        address = self.connections[client_socket]['address'][0]
        username = getpass.getuser()
        password = input(f"Enter password for {username}@{address}: ")

        # Using pypsrp for PowerShell commands
        client = pypsrp.Client(address, username, password)

        # Check if RDP is enabled
        rdp_check_command = "Get-Service -Name TermService"
        result = client.execute_ps(rdp_check_command)
        print(f"RDP Status on {hostname}: {result}")

        # Enable RDP if not enabled
        if "Running" not in result:
            enable_rdp_command = """
            Set-Service -Name TermService -StartupType Automatic
            Start-Service -Name TermService
            """
            print(f"Enabling RDP on {hostname}...")
            client.execute_ps(enable_rdp_command)

    def send_command(self, command):
        for conn in self.connections:
            try:
                conn.sendall(command.encode())
            except Exception as e:
                print(f"Failed to send command: {e}")

    def install_software(self):
        self.send_command("INSTALL")

    def uninstall_software(self):
        self.send_command("UNINSTALL")

    def fix_windows(self):
        self.send_command("FIX_WINDOWS")

    def send_powershell(self):
        command = self.ps_command_entry.get()
        self.send_command(f"POWERSHELL {command}")

if __name__ == "__main__":
    server = Server()

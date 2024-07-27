import socket
import customtkinter as CTk
import threading
import time
import os

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
        self.root.title("OSFM-Net")

        self.install_button = CTk.CTkButton(self.root, text="Install Software", command=self.install_software)
        self.install_button.pack(pady=10)

        self.uninstall_button = CTk.CTkButton(self.root, text="Uninstall Software", command=self.uninstall_software)
        self.uninstall_button.pack(pady=10)

        self.fix_button = CTk.CTkButton(self.root, text="Fix Windows", command=self.fix_windows)
        self.fix_button.pack(pady=10)

        self.powershell_label = CTk.CTkLabel(self.root, text="PowerShell Command:")
        self.powershell_label.pack(pady=5)

        self.powershell_entry = CTk.CTkEntry(self.root, width=400)
        self.powershell_entry.pack(pady=5)

        self.powershell_button = CTk.CTkButton(self.root, text="Send PowerShell Command", command=self.send_powershell)
        self.powershell_button.pack(pady=10)

        self.clients_frame = CTk.CTkFrame(self.root)
        self.clients_frame.pack(pady=10, fill='both', expand=True)

        self.clients_list = CTk.CTkScrollableFrame(self.clients_frame)
        self.clients_list.pack(fill='both', expand=True)

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
                hostname = client_socket.recv(1024).decode()
                self.connections[hostname] = client_socket
                print(f"Client {hostname} ({address}) connected")
                self.update_clients_list()
                threading.Thread(target=self.handle_client, args=(client_socket,), daemon=True).start()
            except Exception as e:
                print(f"TCP server error: {e}")

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode()}")
            except Exception as e:
                print(f"Client connection error: {e}")
                break
        client_socket.close()
        self.update_clients_list()

    def send_command(self, command):
        for conn in self.connections.values():
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
        command = self.powershell_entry.get()
        self.send_command(f"POWERSHELL {command}")

    def update_clients_list(self):
        for widget in self.clients_list.winfo_children():
            widget.destroy()

        for hostname in self.connections.keys():
            button = CTk.CTkButton(self.clients_list, text=hostname, command=lambda h=hostname: self.rdp_to_client(h))
            button.pack(pady=5)

    def rdp_to_client(self, hostname):
        print(f"Initiating RDP to {hostname}")
        os.system(f'mstsc /v:{hostname}')

if __name__ == "__main__":
    server = Server()

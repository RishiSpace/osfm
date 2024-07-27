import socket
import customtkinter as CTk
import threading
import subprocess
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

        self.install_button = CTk.CTkButton(self.root, text="Install Software", command=self.create_install_software_gui)
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

    def search_software(self, search_term):
        if not search_term:
            return

        result = subprocess.run(["winget", "search", search_term], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            lines = result.stdout.splitlines()
            self.software_options = {}
            for line in lines:
                if line.strip() and not line.startswith("Name"):
                    columns = line.split(None, 2)
                    if len(columns) >= 2:
                        software_name = columns[1].strip()
                        software_id = columns[0]
                        self.software_options[software_name] = software_id
            self.display_software_options()
        else:
            print(f"Failed to search for {search_term}: {result.stderr}")

    def display_software_options(self):
        for widget in self.software_buttons_frame.winfo_children():
            widget.destroy()

        for name in self.software_options.keys():
            button = CTk.CTkButton(self.software_buttons_frame, text=name, command=lambda n=name: self.toggle_selection(n))
            button.pack(pady=2, padx=5, fill='x')

    def toggle_selection(self, name):
        if name in self.selected_software:
            self.selected_software.remove(name)
        else:
            self.selected_software.add(name)

    def install_selected_software(self):
        for name in self.selected_software:
            pkg_id = self.software_options[name]
            self.download_software(pkg_id)
        
        self.send_downloaded_software()
        self.send_command("INSTALL_SELECTED")

    def download_software(self, pkg_id):
        try:
            print(f"Downloading software: {pkg_id}")
            result = subprocess.run(["winget", "download", pkg_id], capture_output=True, text=True, encoding='utf-8')
            if result.returncode != 0:
                print(f"Failed to download {pkg_id}: {result.stderr}")
        except Exception as e:
            print(f"Error downloading software {pkg_id}: {e}")

    def send_downloaded_software(self):
        for conn in self.connections.values():
            try:
                for name in self.selected_software:
                    pkg_id = self.software_options[name]
                    file_path = f"{pkg_id}.exe"
                    if os.path.isfile(file_path):
                        with open(file_path, "rb") as file:
                            conn.sendall(f"UPLOAD {file_path}".encode())
                            while (chunk := file.read(4096)):
                                conn.sendall(chunk)
            except Exception as e:
                print(f"Failed to send software to client: {e}")

    def create_install_software_gui(self):
        install_gui = CTk.CTkToplevel(self.root)
        install_gui.geometry("800x600")
        install_gui.title("Install Software")

        search_entry = CTk.CTkEntry(install_gui, placeholder_text="Search for software")
        search_entry.pack(padx=10, pady=5, fill='x')

        search_button = CTk.CTkButton(install_gui, text="Search", command=lambda: self.search_software(search_entry.get()))
        search_button.pack(padx=10, pady=5)

        # Create a frame for the options
        options_frame = CTk.CTkFrame(install_gui)
        options_frame.pack(padx=10, pady=5, fill='both', expand=True)

        # Create a CTkFrame to hold the software options
        self.software_buttons_frame = CTk.CTkFrame(options_frame)
        self.software_buttons_frame.pack(side='left', fill='both', expand=True)

        # Add a canvas and scrollbar
        canvas = CTk.CTkCanvas(options_frame)
        scrollbar = CTk.CTkScrollbar(options_frame, command=canvas.yview)
        scrollbar.pack(side='right', fill='y')

        canvas.pack(side='left', fill='both', expand=True)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Create a frame inside the canvas for the software options
        self.software_options_frame = CTk.CTkFrame(canvas)
        canvas.create_window((0, 0), window=self.software_options_frame, anchor='nw')

        # Update scrollregion to include the entire software options frame
        self.software_options_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        install_button = CTk.CTkButton(install_gui, text="Install Selected", command=self.install_selected_software)
        install_button.pack(padx=10, pady=5, side='bottom')

        self.selected_software = set()

if __name__ == "__main__":
    server = Server()

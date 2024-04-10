import socket
import threading
import customtkinter as ctk
from tkinter import scrolledtext, END

ctk.set_appearance_mode("dark")

class ServerApp:
    @staticmethod
    def get_private_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            IP = s.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            s.close()
        return IP
    
    def __init__(self, root):
        self.clients = {}
        self.root = root
        self.root.title("OSFM Control Panel")
        self.server_running = True

        self.frame_buttons = ctk.CTkFrame(root)
        self.frame_buttons.pack(pady=20)

        self.install_button = ctk.CTkButton(self.frame_buttons, text="Install Software", command=self.install_software)
        self.install_button.pack(side='left', padx=10)

        self.uninstall_button = ctk.CTkButton(self.frame_buttons, text="Uninstall Software", command=self.uninstall_software)
        self.uninstall_button.pack(side='left', padx=10)

        self.fix_button = ctk.CTkButton(self.frame_buttons, text="Fix Windows", command=self.fix_windows)
        self.fix_button.pack(side='left', padx=10)

        self.software_ids_text = ctk.CTkEntry(root, placeholder_text="Enter Winget program IDs separated by commas")
        self.software_ids_text.pack(pady=10)

        self.connected_pcs_text = scrolledtext.ScrolledText(root, height=10, background='black', foreground='white')
        self.connected_pcs_text.pack(pady=10)

        self.powershell_command_text = ctk.CTkEntry(root, placeholder_text="Enter PowerShell command")
        self.powershell_command_text.pack(pady=10)

        self.send_powershell_command_button = ctk.CTkButton(root, text="Send PowerShell Command", command=self.send_powershell_command)
        self.send_powershell_command_button.pack(pady=10)

        self.start_server()

        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = self.get_private_ip()
        port = 12345
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        print(f"Server started on {host}. Waiting for connections...")

        threading.Thread(target=self.accept_connections, daemon=True).start()

    def accept_connections(self):
        while self.server_running:
            try:
                client, address = self.server_socket.accept()
                print(f"Connection from {address} has been established.")

                self.clients[address] = client

                self.connected_pcs_text.insert(END, f"{address}\n")

                threading.Thread(target=self.handle_client, args=(client, address), daemon=True).start()
            except socket.error as e:
                print(f"Error accepting connection: {e}")
                break

    def handle_client(self, client, address):
        while self.server_running:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == "DISCOVERABLE":
                    print(f"{address} is discoverable")
            except socket.error as e:
                print(f"Error receiving message from {address}: {e}")
                break

    def send_command_to_clients(self, command):
        if command.startswith("powershell:"):
            powershell_command = command.split(":", 1)[1]
            for client in self.clients.values():
                try:
                    client.sendall(f"powershell:{powershell_command}".encode('utf-8'))
                except socket.error as e:
                    print(f"Error sending command to client: {e}")
        else:
            for client in self.clients.values():
                try:
                    client.sendall(command.encode('utf-8'))
                except socket.error as e:
                    print(f"Error sending command to client: {e}")


    def install_software(self):
        software_ids = self.software_ids_text.get()
        self.send_command_to_clients(f"install:{software_ids}")

    def uninstall_software(self):
        software_ids = self.software_ids_text.get()
        self.send_command_to_clients(f"uninstall:{software_ids}")

    def fix_windows(self):
        self.send_command_to_clients("fix")

    def send_powershell_command(self):
        powershell_command = self.powershell_command_text.get()
        self.send_command_to_clients(f"powershell:{powershell_command}")

    def on_close(self):
        self.server_running = False
        self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = ServerApp(root)
    root.mainloop()

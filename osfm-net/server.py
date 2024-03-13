import socket
import threading
import customtkinter as ctk
from tkinter import scrolledtext, END

ctk.set_appearance_mode("dark")  # Set the theme of GUI to dark

class ServerApp:
    def __init__(self, root):
        self.clients = {}
        self.root = root
        self.root.title("Server Control Panel")

        # Frame for buttons
        self.frame_buttons = ctk.CTkFrame(root)
        self.frame_buttons.pack(pady=20)

        # Install software button
        self.install_button = ctk.CTkButton(self.frame_buttons, text="Install Software", command=self.install_software)
        self.install_button.pack(side='left', padx=10)

        # Uninstall software button
        self.uninstall_button = ctk.CTkButton(self.frame_buttons, text="Uninstall Software", command=self.uninstall_software)
        self.uninstall_button.pack(side='left', padx=10)

        # Fix Windows button
        self.fix_button = ctk.CTkButton(self.frame_buttons, text="Fix Windows", command=self.fix_windows)
        self.fix_button.pack(side='left', padx=10)

        # Text box for Winget program IDs
        self.software_ids_text = ctk.CTkEntry(root, placeholder_text="Enter Winget program IDs separated by commas")
        self.software_ids_text.pack(pady=10)

        # ScrolledText for displaying connected PCs
        self.connected_pcs_text = scrolledtext.ScrolledText(root, height=10)
        self.connected_pcs_text.pack(pady=10)

        # Start server
        self.start_server()

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        host = socket.gethostname()
        port = 12345
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        print("Server started. Waiting for connections...")

        threading.Thread(target=self.accept_connections).start()

    def accept_connections(self):
        while True:
            client, address = self.server_socket.accept()
            print(f"Connection from {address} has been established.")

            self.clients[address] = client

            self.connected_pcs_text.insert(END, f"{address}\n")

            threading.Thread(target=self.handle_client, args=(client, address)).start()

    def handle_client(self, client, address):
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == "DISCOVERABLE":
                    print(f"{address} is discoverable")
            except:
                print(f"Lost connection to {address}")
                self.clients.pop(address)
                return

    def send_command_to_clients(self, command):
        for client in self.clients.values():
            client.send(command.encode('utf-8'))

    def install_software(self):
        software_ids = self.software_ids_text.get()
        self.send_command_to_clients(f"install:{software_ids}")

    def uninstall_software(self):
        software_ids = self.software_ids_text.get()
        self.send_command_to_clients(f"uninstall:{software_ids}")

    def fix_windows(self):
        self.send_command_to_clients("fix")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ServerApp(root)
    root.mainloop()

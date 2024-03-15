import socket
import threading
import customtkinter as ctk
from tkinter import scrolledtext, END, filedialog
import os

ctk.set_appearance_mode("dark")  # Set the theme of GUI to dark

class ServerApp:
    @staticmethod
    def get_private_ip():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # doesn't even have to be reachable
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
        self.connected_pcs_text = scrolledtext.ScrolledText(root, height=10, background='black', foreground='white')
        self.connected_pcs_text.pack(pady=10)

        # Button for selecting files or folders to send
        self.file_transfer_button = ctk.CTkButton(root, text="Transfer Files", command=self.select_files)
        self.file_transfer_button.pack(pady=10)

        # Start server
        self.start_server()

        # Bind the GUI close event
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
            self.server_socket.settimeout(1.0)  # Set timeout for the accept call
            try:
                client, address = self.server_socket.accept()
                print(f"Connection from {address} has been established.")

                self.clients[address] = client

                self.connected_pcs_text.insert(END, f"{address}\n")

                threading.Thread(target=self.handle_client, args=(client, address), daemon=True).start()
            except socket.timeout:
                continue

    def handle_client(self, client, address):
        while self.server_running:
            try:
                message = client.recv(1024).decode('utf-8')
                if message == "DISCOVERABLE":
                    print(f"{address} is discoverable")
            except:
                print(f"Lost connection to {address}")
                self.clients.pop(address, None)
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

    def select_files(self):
        file_paths = filedialog.askopenfilenames(title="Select files")
        folder_paths = filedialog.askdirectory(title="Select folders")  # This allows only one folder to be selected at a time
        self.transfer_files_to_clients(file_paths, folder_paths)

    def transfer_files_to_clients(self, file_paths, folder_paths):
        for client in self.clients.values():
            # First, send a signal to prepare the client for file transfer
            client.send("FILE_TRANSFER_INIT".encode('utf-8'))
            
            # Send files
            for file_path in file_paths:
                self.send_file(client, file_path)
            
            # If folders are selected, send each file in the folder
            if folder_paths:
                for root, dirs, files in os.walk(folder_paths):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.send_file(client, file_path)
            
            # Signal the end of file transfer
            client.send("FILE_TRANSFER_COMPLETE".encode('utf-8'))

    def send_file(self, client, file_path):
        # Send the file name first
        client.send(f"FILE:{os.path.basename(file_path)}".encode('utf-8'))
        # Then send the file size
        file_size = os.path.getsize(file_path)
        client.send(f"SIZE:{file_size}".encode('utf-8'))
        
        # Finally, send the file content
        with open(file_path, 'rb') as file:
            content = file.read(1024)
            while content:
                client.send(content)
                content = file.read(1024)

    def on_close(self):
        self.server_running = False
        self.server_socket.close()
        self.root.destroy()

if __name__ == "__main__":
    root = ctk.CTk()
    app = ServerApp(root)
    root.mainloop()
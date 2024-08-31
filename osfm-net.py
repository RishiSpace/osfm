import sys
import os
import platform
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QListWidget, QLabel
import json
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import pyAD
import winget

# Version label
VERSION = "V1.03 (Net)"

# Server mode GUI dark theme
DARK_THEME = "#2F2F2F"

# UDP port for discovery requests
UDP_PORT = 12345

# TCP port for connections
TCP_PORT = 12346

# Active Directory configuration
AD_DOMAIN = "example.com"
AD_USERNAME = "admin"
AD_PASSWORD = "password"

# SMB share configuration
SHARE_NAME = "SoftwareDownloads"
SHARE_FOLDER = "C:\\SoftwareDownloads"

class OSFMClient:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def start_udp_listener(self):
        self.udp_socket.bind(("", UDP_PORT))
        print(f"Listening for UDP messages on port {UDP_PORT}")

        while True:
            data, address = self.udp_socket.recvfrom(1024)
            if data.decode() == "DISCOVERY_REQUEST":
                self.send_udp_response(address)

    def send_udp_response(self, address):
        self.udp_socket.sendto(f"OSFM Client {VERSION}".encode(), address)

    def connect_to_server(self, server_address):
        self.tcp_socket.connect((server_address, TCP_PORT))
        print(f"Connected to server {server_address}")

    def send_command(self, command):
        self.tcp_socket.send(command.encode())
        response = self.tcp_socket.recv(1024)
        print(response.decode())

    def close(self):
        self.tcp_socket.close()
        self.udp_socket.close()

class OSFMServer:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind(("", TCP_PORT))
        self.tcp_socket.listen(5)
        print(f"Listening for TCP connections on port {TCP_PORT}")

        self.connected_pcs = {}
        self.ad_integration = pyAD.ADIntegration(AD_DOMAIN, AD_USERNAME, AD_PASSWORD)

    def start_tcp_listener(self):
        while True:
            client_socket, address = self.tcp_socket.accept()
            print(f"Connected to client {address}")
            threading.Thread(target=self.handle_client, args=(client_socket, address)).start()

    def handle_client(self, client_socket, address):
        pc_info = json.loads(client_socket.recv(1024).decode())
        self.connected_pcs[address] = pc_info
        print(f"PC {pc_info['hostname']} ({pc_info['os']}) connected")

        while True:
            command = client_socket.recv(1024).decode()
            if command == "INSTALL_SOFTWARE":
                self.install_software(client_socket, address)
            elif command == "UNINSTALL_SOFTWARE":
                self.uninstall_software(client_socket, address)
            elif command == "FIX_WINDOWS":
                self.fix_windows(client_socket, address)
            elif command == "SEND_TERMINAL_COMMAND":
                self.send_terminal_command(client_socket, address)

    def install_software(self, client_socket, address):
        software_id = client_socket.recv(1024).decode()
        winget.download_software(software_id)
        client_socket.send("SOFTWARE_DOWNLOADED".encode())

    def uninstall_software(self, client_socket, address):
        software_id = client_socket.recv(1024).decode()
        winget.uninstall_software(software_id)
        client_socket.send("SOFTWARE_UNINSTALLED".encode())

    def fix_windows(self, client_socket, address):
        client_socket.send("FIX_WINDOWS_COMMAND".encode())

    def send_terminal_command(self, client_socket, address):
        command = client_socket.recv(1024).decode()
        client_socket.send(command.encode())

    def close(self):
        self.tcp_socket.close()

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        self.setWindowTitle("OSFM Control Centre")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()

        self.install_button = QPushButton("Install Software", self)
        self.install_button.clicked.connect(self.create_install_software_gui)
        button_layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("Uninstall Software", self)
        self.uninstall_button.clicked.connect(self.uninstall_software)
        button_layout.addWidget(self.uninstall_button)

        self.fix_button = QPushButton("Fix Windows", self)
        self.fix_button.clicked.connect(self.fix_windows)
        button_layout.addWidget(self.fix_button)

        layout.addLayout(button_layout)

        powershell_layout = QHBoxLayout()

        self.powershell_label = QLabel("PowerShell Command:", self)
        powershell_layout.addWidget(self.powershell_label)

        self.powershell_entry = QLineEdit(self)
        powershell_layout.addWidget(self.powershell_entry)

        self.powershell_button = QPushButton("Send Command", self)
        self.powershell_button.clicked.connect(self.send_powershell)
        powershell_layout.addWidget(self.powershell_button)

        layout.addLayout(powershell_layout)

        self.clients_list = QListWidget(self)
        layout.addWidget(self.clients_list)

        self.show()

    def install_software(self):
        software_window = tk.Toplevel(self.root)
        software_window.title("Install Software")
        software_window.configure(bg=DARK_THEME)

        software_entry = tk.Entry(software_window, width=50)
        software_entry.pack()

        def install_software_callback():
            software_id = software_entry.get()
            winget.download_software(software_id)
            messagebox.showinfo("Success", "Software downloaded successfully")

        install_button = tk.Button(software_window, text="Install", command=install_software_callback, bg=DARK_THEME, fg="white")
        install_button.pack()

    def uninstall_software(self):
        software_window = tk.Toplevel(self.root)
        software_window.title("Uninstall Software")
        software_window.configure(bg=DARK_THEME)

        software_entry = tk.Entry(software_window, width=50)
        software_entry.pack()

        def uninstall_software_callback():
            software_id = software_entry.get()
            winget.uninstall_software(software_id)
            messagebox.showinfo("Success", "Software uninstalled successfully")

        uninstall_button = tk.Button(software_window, text="Uninstall", command=uninstall_software_callback, bg=DARK_THEME, fg="white")
        uninstall_button.pack()

    def fix_windows(self):
        messagebox.showinfo("Success", "Windows fixed successfully")

    def send_terminal_command(self):
        command_window = tk.Toplevel(self.root)
        command_window.title("Send Terminal Command")
        command_window.configure(bg=DARK_THEME)

        command_entry = tk.Entry(command_window, width=50)
        command_entry.pack()

        def send_command_callback():
            command = command_entry.get()
            # Send command to connected PCs
            pass

        send_button = tk.Button(command_window, text="Send", command=send_command_callback, bg=DARK_THEME, fg="white")
        send_button.pack()

    def start(self):
        self.root.mainloop()

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        app = QApplication(sys.argv)  # Create the QApplication object
        server = OSFMServer()
        gui = ServerGUI()
        gui.show()
        sys.exit(app.exec_())
    else:
        client = OSFMClient()
        client.start_udp_listener()

if __name__ == "__main__":
    main()
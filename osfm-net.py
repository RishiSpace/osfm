import sys
import os
import socket
import json
import threading
import time
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, 
                              QListWidget, QLabel, QTextEdit, QDialog, QFormLayout, QMessageBox)

# Constants
VERSION = "V1.03 (Net)"
UDP_PORT = 12345
TCP_PORT = 12346
SERVER_LOCK_FILE = "server.lock"

class OSFMClient:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = None

    def start_udp_broadcast(self):
        while True:
            message = f"DISCOVERY_REQUEST {VERSION}".encode()
            self.udp_socket.sendto(message, ('<broadcast>', UDP_PORT))
            time.sleep(5)  # Broadcast every 5 seconds

    def start_udp_listener(self):
        self.udp_socket.bind(("", UDP_PORT))
        print(f"Listening for UDP messages on port {UDP_PORT}")

        while True:
            data, address = self.udp_socket.recvfrom(1024)
            if data.decode().startswith("OSFM Server"):
                self.server_address = address[0]
                print(f"Discovered server at {self.server_address}")
                self.connect_to_server(self.server_address)

    def connect_to_server(self, server_address):
        try:
            self.tcp_socket.connect((server_address, TCP_PORT))
            print(f"Connected to server {server_address}")
        except Exception as e:
            print(f"Failed to connect to server: {e}")

    def send_command(self, command):
        if self.tcp_socket:
            try:
                self.tcp_socket.send(command.encode())
                response = self.tcp_socket.recv(1024).decode()
                print(response)
            except Exception as e:
                print(f"Failed to send command: {e}")

    def close(self):
        if self.tcp_socket:
            self.tcp_socket.close()
        self.udp_socket.close()

    def start(self):
        threading.Thread(target=self.start_udp_broadcast, daemon=True).start()
        threading.Thread(target=self.start_udp_listener, daemon=True).start()
        # Keep the client running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.close()

    def check_for_server(self):
        return os.path.isfile(SERVER_LOCK_FILE)

class ServerGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.client_socket = None

    def setup_ui(self):
        self.setWindowTitle("OSFM Control Centre")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        button_layout = QHBoxLayout()

        self.install_button = QPushButton("Install Software", self)
        self.install_button.clicked.connect(self.open_install_software_dialog)
        button_layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton("Uninstall Software", self)
        self.uninstall_button.clicked.connect(self.open_uninstall_software_dialog)
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

    def connect_to_server(self):
        if self.client_socket is not None:
            self.client_socket.close()
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(('localhost', TCP_PORT))

    def open_install_software_dialog(self):
        self._open_software_dialog("Install Software", self.install_software)

    def open_uninstall_software_dialog(self):
        self._open_software_dialog("Uninstall Software", self.uninstall_software)

    def _open_software_dialog(self, title, action_callback):
        dialog = QDialog(self)
        dialog.setWindowTitle(title)
        layout = QVBoxLayout()
        dialog.setLayout(layout)

        form_layout = QFormLayout()
        self.software_entry = QLineEdit()
        form_layout.addRow(QLabel("Software ID:"), self.software_entry)

        self.output_box = QTextEdit()
        self.output_box.setReadOnly(True)
        form_layout.addRow(QLabel("Output:"), self.output_box)

        layout.addLayout(form_layout)

        action_button = QPushButton(title, self)
        action_button.clicked.connect(action_callback)
        layout.addWidget(action_button)

        dialog.exec_()

    def install_software(self):
        software_id = self.software_entry.text()
        self.output_box.append(f"Starting installation of software ID: {software_id}")
        result = self._send_command_to_server(f"INSTALL_SOFTWARE:{software_id}")
        self.output_box.append(f"Installation result: {result}")

    def uninstall_software(self):
        software_id = self.software_entry.text()
        self.output_box.append(f"Starting uninstallation of software ID: {software_id}")
        result = self._send_command_to_server(f"UNINSTALL_SOFTWARE:{software_id}")
        self.output_box.append(f"Uninstallation result: {result}")

    def fix_windows(self):
        result = self._send_command_to_server("FIX_WINDOWS")
        QMessageBox.information(self, "Success", result)

    def send_powershell(self):
        command = self.powershell_entry.text()
        self.output_box.append(f"Sending PowerShell command: {command}")
        result = self._send_command_to_server(f"SEND_TERMINAL_COMMAND:{command}")
        self.output_box.append(f"Command result: {result}")

    def _send_command_to_server(self, command):
        try:
            self.connect_to_server()
            self.client_socket.send(command.encode())
            response = self.client_socket.recv(1024).decode()
            self.client_socket.close()
            return response
        except Exception as e:
            return f"Error: {str(e)}"

class OSFMServer:
    def __init__(self):
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.tcp_socket.bind(("", TCP_PORT))
        self.tcp_socket.listen(5)
        print(f"Listening for TCP connections on port {TCP_PORT}")

        self.connected_pcs = {}
        self.ad_integration = None  # Add AD Integration if needed

    def start_udp_broadcast(self):
        while True:
            message = f"OSFM Server {VERSION}".encode()
            self.udp_socket.sendto(message, ('<broadcast>', UDP_PORT))
            time.sleep(5)  # Broadcast every 5 seconds

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
            if command.startswith("INSTALL_SOFTWARE"):
                self.install_software(client_socket, address, command)
            elif command.startswith("UNINSTALL_SOFTWARE"):
                self.uninstall_software(client_socket, address, command)
            elif command == "FIX_WINDOWS":
                self.fix_windows(client_socket, address)
            elif command.startswith("SEND_TERMINAL_COMMAND"):
                self.send_terminal_command(client_socket, address, command)

    def install_software(self, client_socket, address, command):
        software_id = command.split(':')[1]
        # Simulate software installation
        print(f"Installing software with ID: {software_id}")
        result = f"Software with ID {software_id} installed."
        client_socket.send(result.encode())

    def uninstall_software(self, client_socket, address, command):
        software_id = command.split(':')[1]
        # Simulate software uninstallation
        print(f"Uninstalling software with ID: {software_id}")
        result = f"Software with ID {software_id} uninstalled."
        client_socket.send(result.encode())

    def fix_windows(self, client_socket, address):
        print(f"Fixing Windows for {address}")
        # Simulate Windows fix
        result = "Windows fixed successfully."
        client_socket.send(result.encode())

    def send_terminal_command(self, client_socket, address, command):
        command_text = command.split(':')[1]
        print(f"Executing command on {address}: {command_text}")
        result = self._execute_command_on_target(command_text)
        client_socket.send(result.encode())

    def _execute_command_on_target(self, command):
        # Execute a command on the target machine and return the result
        try:
            result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
            return f"Command executed successfully: {result}"
        except subprocess.CalledProcessError as e:
            return f"Command failed: {e.output}"

    def close(self):
        self.tcp_socket.close()
        self.udp_socket.close()

    def start(self):
        if os.path.isfile(SERVER_LOCK_FILE):
            print("Server is already running. Exiting...")
            sys.exit(1)
        else:
            with open(SERVER_LOCK_FILE, 'w') as lock_file:
                lock_file.write(str(os.getpid()))

            try:
                threading.Thread(target=self.start_udp_broadcast, daemon=True).start()
                app = QApplication(sys.argv)
                gui = ServerGUI()
                gui.show()
                app.exec_()
            finally:
                os.remove(SERVER_LOCK_FILE)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--server":
        client = OSFMClient()
        if client.check_for_server():
            print("Upgrading existing client to server mode.")
            client.close()
            server = OSFMServer()
            server.start()
        else:
            server = OSFMServer()
            server.start()
    else:
        client = OSFMClient()
        client.start()

if __name__ == "__main__":
    main()

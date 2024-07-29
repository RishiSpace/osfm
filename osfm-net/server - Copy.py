import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QScrollArea, QFrame, QGridLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor
import socket
import threading
import subprocess
import os

class Server(QWidget):
    def __init__(self):
        super().__init__()

        self.server_ip = "0.0.0.0"
        self.server_port = 12345
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.connections = {}

        self.initUI()
        self.start_udp_listener()
        self.start_tcp_server()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('OSFM-Net')

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.install_button = QPushButton('Install Software')
        self.install_button.clicked.connect(self.create_install_software_gui)
        self.layout.addWidget(self.install_button)

        self.uninstall_button = QPushButton('Uninstall Software')
        self.uninstall_button.clicked.connect(self.uninstall_software)
        self.layout.addWidget(self.uninstall_button)

        self.fix_button = QPushButton('Fix Windows')
        self.fix_button.clicked.connect(self.fix_windows)
        self.layout.addWidget(self.fix_button)

        self.powershell_label = QLabel('PowerShell Command:')
        self.layout.addWidget(self.powershell_label)

        self.powershell_entry = QLineEdit()
        self.layout.addWidget(self.powershell_entry)

        self.powershell_button = QPushButton('Send PowerShell Command')
        self.powershell_button.clicked.connect(self.send_powershell)
        self.layout.addWidget(self.powershell_button)

        self.clients_frame = QFrame()
        self.clients_frame.setLayout(QGridLayout())
        self.layout.addWidget(self.clients_frame)

        self.clients_list = QScrollArea()
        self.clients_list.setWidgetResizable(True)
        self.clients_frame.layout().addWidget(self.clients_list)

        self.software_buttons_frame = QFrame()
        self.software_buttons_frame.setLayout(QGridLayout())
        self.clients_list.setWidget(self.software_buttons_frame)

        self.selected_software = set()

    def create_install_software_gui(self):
        install_gui = QWidget()
        install_gui.setWindowTitle('Install Software')

        layout = QVBoxLayout()
        install_gui.setLayout(layout)

        search_entry = QLineEdit()
        search_entry.setPlaceholderText('Search for software')
        layout.addWidget(search_entry)

        search_button = QPushButton('Search')
        search_button.clicked.connect(lambda: self.search_software(search_entry.text()))
        layout.addWidget(search_button)

        options_frame = QFrame()
        options_frame.setLayout(QGridLayout())
        layout.addWidget(options_frame)

        self.software_options_frame = QFrame()
        self.software_options_frame.setLayout(QGridLayout())
        options_frame.layout().addWidget(self.software_options_frame)

        install_button = QPushButton('Install Selected')
        install_button.clicked.connect(self.install_selected_software)
        layout.addWidget(install_button)

        install_gui.show()

    def start_udp_listener(self):
        udp_thread = threading.Thread(target=self.udp_listener)
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
        tcp_thread = threading.Thread(target=self.tcp_server)
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
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()
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
        command = self.powershell_entry.text()
        self.send_command(f"POWERSHELL {command}")

    def update_clients_list(self):
        for i in range(self.clients_frame.layout().count()):
            self.clients_frame.layout().itemAt(i).widget().deleteLater()

        for hostname in self.connections.keys():
            button = QPushButton(hostname)
            button.clicked.connect(lambda hostname=hostname: self.rdp_to_client(hostname))
            self.clients_frame.layout().addWidget(button)

    def rdp_to_client(self, hostname):
        print(f"Initiating RDP to {hostname}")
        subprocess.run(['mstsc', '/v:' + hostname])

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
        for i in range(self.software_options_frame.layout().count()):
            self.software_options_frame.layout().itemAt(i).widget().deleteLater()

        for name in self.software_options.keys():
            button = QPushButton(name)
            button.clicked.connect(lambda name=name: self.toggle_selection(name))
            self.software_options_frame.layout().addWidget(button)

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
            subprocess.run(["winget", "download", pkg_id], capture_output=True, text=True, encoding='utf-8')
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
                            while True:
                                chunk = file.read(4096)
                                if not chunk:
                                    break
                                conn.sendall(chunk)
            except Exception as e:
                print(f"Failed to send software to client: {e}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.white)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    server = Server()
    server.show()
    sys.exit(app.exec_())
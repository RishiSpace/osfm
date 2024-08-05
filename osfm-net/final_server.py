import subprocess
import socket
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import os

host = subprocess.getoutput("hostname")  # Correctly fetch hostname

class Server(QtWidgets.QMainWindow):
    
    def __init__(self, host="0.0.0.0", port=12345):
        super().__init__()
        self.server_ip = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.connections = {}
        self.network_share_path = r"\\NETWORK_SHARE\path\to\folder"  # Ensure this path is accessible
        self.setup_ui()
        self.start_udp_listener()
        self.start_tcp_server()

    def setup_ui(self):
        self.setWindowTitle("OSFM Control Centre")
        self.setGeometry(100, 100, 800, 600)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)

        layout = QtWidgets.QVBoxLayout(central_widget)

        button_layout = QtWidgets.QHBoxLayout()

        self.install_button = QtWidgets.QPushButton("Install Software", self)
        self.install_button.clicked.connect(self.create_install_software_gui)
        button_layout.addWidget(self.install_button)

        self.uninstall_button = QtWidgets.QPushButton("Uninstall Software", self)
        self.uninstall_button.clicked.connect(self.uninstall_software)
        button_layout.addWidget(self.uninstall_button)

        self.fix_button = QtWidgets.QPushButton("Fix Windows", self)
        self.fix_button.clicked.connect(self.fix_windows)
        button_layout.addWidget(self.fix_button)

        layout.addLayout(button_layout)

        powershell_layout = QtWidgets.QHBoxLayout()

        self.powershell_label = QtWidgets.QLabel("PowerShell Command:", self)
        powershell_layout.addWidget(self.powershell_label)

        self.powershell_entry = QtWidgets.QLineEdit(self)
        powershell_layout.addWidget(self.powershell_entry)

        self.powershell_button = QtWidgets.QPushButton("Send Command", self)
        self.powershell_button.clicked.connect(self.send_powershell)
        powershell_layout.addWidget(self.powershell_button)

        layout.addLayout(powershell_layout)

        self.clients_list = QtWidgets.QListWidget(self)
        layout.addWidget(self.clients_list)

        self.show()

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
                self.send_command(host)
                self.update_clients_list()
                threading.Thread(target=self.handle_client, args=(client_socket, hostname), daemon=True).start()
            except Exception as e:
                print(f"TCP server error: {e}")

    def handle_client(self, client_socket, hostname):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received from {hostname}: {data.decode()}")
                if data.startswith(b"UPLOAD"):
                    self.receive_file(client_socket)
                elif data.startswith(b"FILE_PATH"):
                    file_path = data.decode().split(" ", 1)[1]
                    self.handle_file_path(file_path)
            except Exception as e:
                print(f"Client connection error: {e}")
                break
        client_socket.close()
        if hostname in self.connections:
            del self.connections[hostname]
        self.update_clients_list()

    def receive_file(self, client_socket):
        try:
            file_name = client_socket.recv(1024).decode()
            file_path = os.path.join(self.network_share_path, file_name)

            if not os.path.exists(self.network_share_path):
                os.makedirs(self.network_share_path)

            with open(file_path, "wb") as f:
                while True:
                    data = client_socket.recv(4096)
                    if data == b"END_OF_FILE":
                        break
                    f.write(data)

            print(f"File received and saved to {file_path}")
        except Exception as e:
            print(f"Error receiving file: {e}")

    def handle_file_path(self, file_path):
        print(f"Handling file path: {file_path}")
        # Additional processing if needed

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
        self.clients_list.clear()
        for hostname in self.connections.keys():
            item = QtWidgets.QListWidgetItem(hostname)
            self.clients_list.addItem(item)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.UserRole, hostname)
        self.clients_list.itemDoubleClicked.connect(self.rdp_to_client)

    def rdp_to_client(self, item):
        hostname = item.data(QtCore.Qt.UserRole)
        print(f"Initiating RDP to {hostname}")
        os.system(f'mstsc /v:{hostname}')

    def search_software(self, search_term):
        if not search_term:
            return

        result = subprocess.run(["winget", "search", search_term, "--source", "winget"], capture_output=True, text=True, encoding='utf-8')
        if result.returncode == 0:
            self.software_options = self.parse_winget_output(result.stdout)
            self.display_software_options()
        else:
            print(f"Failed to search for {search_term}: {result.stderr}")

    def parse_winget_output(self, output):
        lines = output.strip().split('\n')
        software_options = {}

        header_index = next((i for i, line in enumerate(lines) if 'Name' in line), None)
        if header_index is None:
            return software_options

        header_line = lines[header_index]
        name_pos = header_line.index('Name')
        id_pos = header_line.index('Id')
        version_pos = header_line.index('Version')
        match_pos = header_line.index('Match') if 'Match' in header_line else None
        source_pos = header_line.index('Source') if 'Source' in header_line else None

        for line in lines[header_index + 2:]:
            if source_pos:
                name = line[name_pos:id_pos].strip()
                id_ = line[id_pos:version_pos].strip()
                version = line[version_pos:match_pos].strip() if match_pos else line[version_pos:source_pos].strip()
                match = line[match_pos:source_pos].strip() if match_pos else ''
                source = line[source_pos:].strip()
            elif match_pos:
                name = line[name_pos:id_pos].strip()
                id_ = line[id_pos:version_pos].strip()
                version = line[version_pos:match_pos].strip()
                match = line[match_pos:].strip()
                source = ''
            else:
                name = line[name_pos:id_pos].strip()
                id_ = line[id_pos:version_pos].strip()
                version = line[version_pos:].strip()
                match = ''
                source = ''

            software_options[name] = id_

        return software_options

    def display_software_options(self):
        self.software_buttons_frame.clear()
        for name in self.software_options.keys():
            item = QtWidgets.QListWidgetItem(name)
            self.software_buttons_frame.addItem(item)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.UserRole, name)

    def toggle_selection(self, item):
        name = item.data(QtCore.Qt.UserRole)
        if name in self.selected_software:
            self.selected_software.remove(name)
        else:
            self.selected_software.add(name)

    def install_selected_software(self):
        for name in self.selected_software:
            pkg_id = self.software_options[name]
            self.download_software(pkg_id)
            for hostname in self.connections:
                self.send_download_path(pkg_id, host, hostname)

        self.send_command("INSTALL")

    def download_software(self, pkg_id):
        print(f"Downloading software: {pkg_id}")
        download_path = f"temp/{pkg_id}"
        result = subprocess.run(["winget", "download", "--id", pkg_id, "-d", download_path ], capture_output=True, text=True, encoding='utf-8')
        if result.returncode != 0:
            print(f"Failed to download {pkg_id}: {result.stderr}")
        else:
            print(f"Successfully downloaded {pkg_id}")

    def send_download_path(self, pkg_id, host, hostname):
        file_path = self.find_downloaded_file(pkg_id)
        if file_path:
           
            # Format the path as 'hostname\path'
            formatted_path = f"\\{host}\\temp\\{pkg_id}"
            command = f"FILE_PATH {formatted_path}"
            if hostname in self.connections:
                try:
                    self.connections[hostname].sendall(command.encode())
                    print(f"Sent file path to {hostname}: {formatted_path}")
                except Exception as e:
                    print(f"Failed to send file path to {hostname}: {e}")
            else:
                print(f"Client {hostname} not connected")
        else:
            print(f"No file found for package ID: {pkg_id}")

    def find_downloaded_file(self, pkg_id):
        package_dir = os.path.join("temp", pkg_id)
        if os.path.exists(package_dir):
            for file in os.listdir(package_dir):
                if file.endswith(".exe") or file.endswith(".msi"):
                    return os.path.join(package_dir, file)
        return None

    def create_install_software_gui(self):
        install_gui = QtWidgets.QDialog(self)
        install_gui.setWindowTitle("Install Software")
        install_gui.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(install_gui)

        search_layout = QtWidgets.QHBoxLayout()
        self.search_entry = QtWidgets.QLineEdit(install_gui)
        self.search_entry.setPlaceholderText("Search for software")
        search_layout.addWidget(self.search_entry)

        search_button = QtWidgets.QPushButton("Search", install_gui)
        search_button.clicked.connect(lambda: self.search_software(self.search_entry.text()))
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        self.software_buttons_frame = QtWidgets.QListWidget(install_gui)
        self.software_buttons_frame.itemClicked.connect(self.toggle_selection)
        layout.addWidget(self.software_buttons_frame)

        install_button = QtWidgets.QPushButton("Install Selected", install_gui)
        install_button.clicked.connect(self.install_selected_software)
        layout.addWidget(install_button)

        self.selected_software = set()

        install_gui.exec_()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(15, 15, 15))  
    palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)  
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25,25,25))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))  
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)  
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)  
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)  
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))  
    palette.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.white)  
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)  
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))  
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))  
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)  

    app.setPalette(palette)

    app.setStyleSheet("""
        QPushButton {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #444444;
        }
        QPushButton:pressed {
            background-color: #555555;
        }
        QListWidget {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 5px;
        }
        QListWidget:item {
            padding: 5px;
        }
        QListWidget:item:selected {
            background-color: #444444;
        }
        QLineEdit {
            background-color: #333333;
            color: #FFFFFF;
            border: 1px solid #555555;
            padding: 5px;
            border-radius: 5px;
        }
    """)

    server = Server()
    sys.exit(app.exec_())
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
        self.uninstall_button.clicked.connect(self.create_uninstall_software_gui)
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
                elif data.startswith(b"UNINSTALL"):
                    software_id = data.decode().split(" ", 1)[1]
                    self.uninstall_software(software_id)
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

    def uninstall_software(self, software_id):
        self.send_command(f"UNINSTALL {software_id}")

    def fix_windows(self):
        self.send_command("FIX_WINDOWS")

    def send_powershell(self):
        command = self.powershell_entry.text()
        self.send_command(f"POWERSHELL {command}")

    def update_clients_list(self):
        self.clients_list.clear()
        for hostname in self.connections.keys():
            hostname = hostname.replace("HOSTNAME ", "")
            item = QtWidgets.QListWidgetItem(hostname)
            self.clients_list.addItem(item)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEnabled)
            item.setData(QtCore.Qt.UserRole, hostname)
        self.clients_list.itemDoubleClicked.connect(self.rdp_to_client)

    def rdp_to_client(self, item):
        hostname = item.data(QtCore.Qt.UserRole)
        hostname = hostname.replace("HOSTNAME ", "")
        print(f"Initiating RDP to {hostname}")
        os.system(f'mstsc /v:{hostname}')

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

    def create_uninstall_software_gui(self):
        uninstall_gui = QtWidgets.QDialog(self)
        uninstall_gui.setWindowTitle("Uninstall Software")
        uninstall_gui.setGeometry(100, 100, 800, 600)

        layout = QtWidgets.QVBoxLayout(uninstall_gui)

        self.uninstall_entry = QtWidgets.QLineEdit(uninstall_gui)
        self.uninstall_entry.setPlaceholderText("Enter software ID to uninstall")
        layout.addWidget(self.uninstall_entry)

        uninstall_button = QtWidgets.QPushButton("Uninstall", uninstall_gui)
        uninstall_button.clicked.connect(self.trigger_uninstall)
        layout.addWidget(uninstall_button)

        uninstall_gui.exec_()

    def trigger_uninstall(self):
        software_id = self.uninstall_entry.text()
        if software_id:
            self.uninstall_software(software_id)
        else:
            print("Please enter a software ID.")

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

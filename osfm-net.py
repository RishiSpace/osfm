import subprocess
import socket
import time
import os
import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import threading

def signal_handler(sig, frame):
    print("Exiting gracefully...")
    sys.exit(0)

host = ""
# Check for existing server instance
def is_server_running(port=12345):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', port))
            return False  # Port is available, no server is running
    except socket.error:
        return True  # Port is in use, server is running
    
# Get the local hostname
def get_local_hostname():
    return socket.gethostname()

# Server class definition
class Server(QtWidgets.QMainWindow):
    def __init__(self, host="0.0.0.0", port=12345):
        super().__init__()
        self.server_ip = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.connections = {}
        self.network_share_path = r"\\NETWORK_SHARE\path\to\folder"
        self.setup_ui()
        self.start_udp_listener()
        self.start_tcp_server()
        self.apply_styling()


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

    def install_software(self):
        self.send_command("INSTALL")

    def uninstall_software(self):
        self.send_command("UNINSTALL")

    def fix_windows(self):
        try:
            # 1. Run System File Checker (sfc)
            print("Running System File Checker (sfc)...")
            sfc_result = subprocess.run(["sfc", "/scannow"], capture_output=True, text=True)
            if sfc_result.returncode == 0:
                print("sfc completed successfully.")
                print(sfc_result.stdout)
            else:
                print("sfc encountered an error.")
                print(sfc_result.stderr)

            # 2. Run DISM to check the health of the Windows image
            print("Running DISM to check the health of the Windows image...")
            dism_check = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/CheckHealth"], capture_output=True, text=True)
            print(dism_check.stdout)
            
            # 3. Run DISM to scan the Windows image for corruption
            print("Running DISM to scan the Windows image for corruption...")
            dism_scan = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/ScanHealth"], capture_output=True, text=True)
            print(dism_scan.stdout)
            
            # 4. Run DISM to repair the Windows image
            print("Running DISM to repair the Windows image...")
            dism_repair = subprocess.run(["DISM", "/Online", "/Cleanup-Image", "/RestoreHealth"], capture_output=True, text=True)
            print(dism_repair.stdout)

            print("Windows fix process completed.")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e.stderr}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

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

    def search_software(self, search_term):
        if not search_term:
            return

        result = subprocess.run(["winget", "search", search_term, "--source", "winget"], capture_output=True, text=True)
        if result.returncode == 0:
            self.software_options = self.parse_winget_output(result.stdout)
            print("Software options:", self.software_options)  # Debugging line
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
                software_options[name] = id_
            elif match_pos:
                name = line[name_pos:id_pos].strip()
                id_ = line[id_pos:version_pos].strip()
                software_options[name] = id_
            else:
                name = line[name_pos:id_pos].strip()
                id_ = line[id_pos:version_pos].strip()
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
            if name not in self.software_options:
                print(f"Software '{name}' not found in options.")
                continue

            pkg_id = self.software_options[name]
            self.download_software(pkg_id)
            for hostname in self.connections:
                self.send_download_path(pkg_id, host, hostname)

        self.send_command("INSTALL")

    def download_software(self, pkg_id):
        print(f"Downloading software: {pkg_id}")
        download_path = f"temp/{pkg_id}"
        result = subprocess.run(["winget", "download", "--id", pkg_id, "-d", download_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to download {pkg_id}: {result.stderr}")
        else:
            print(f"Successfully downloaded {pkg_id}")

    def send_download_path(self, pkg_id, host, hostname):
        file_path = self.find_downloaded_file(pkg_id)
        if file_path:
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
    
    def apply_styling(self):
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.Window, QtGui.QColor(15, 15, 15))  
        palette.setColor(QtGui.QPalette.WindowText, QtCore.Qt.white)  
        palette.setColor(QtGui.QPalette.Base, QtGui.QColor(25, 25, 25))
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

        self.setPalette(palette)

        self.setStyleSheet(""" 
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

def uninstall_software(software_id):
    try:
        print(f"Uninstalling software with ID: {software_id}")
        result = subprocess.run(["winget", "uninstall", "--id", software_id], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"Uninstall succeeded: {result.stdout}")
        else:
            print(f"Uninstall failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Uninstall command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while uninstalling software: {e}")

def execute_command(command):
    try:
        print(f"Executing command: {command}")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Command succeeded: {result.stdout}")
        else:
            print(f"Command failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Command execution failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while executing command: {e}")

# Get the current network category (Private/Public)
def get_network_category():
    try:
        result = subprocess.run(
            ["powershell", "-Command", "Get-NetConnectionProfile | Select-Object -ExpandProperty NetworkCategory"],
            capture_output=True, text=True, check=True
        )
        network_category = result.stdout.strip()
        print(f"Current network category: {network_category}")
        return network_category
    except subprocess.CalledProcessError as e:
        print(f"Error getting network category: {e}")
        return None

# Change the network profile to Private
def change_network_to_private():
    try:
        print("Attempting to change network profile to Private...")
        command = (
            "Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -eq 'Public'} | "
            "Set-NetConnectionProfile -NetworkCategory Private"
        )
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        print(f"Network profile changed to Private. Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error changing network profile: {e}")
        print(f"Error output: {e.stderr}")
        return False

# Check if Remote Desktop Protocol (RDP) is enabled
def check_rdp_status():
    try:
        command = r"Get-ItemProperty -Path 'HKLM:\System\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' | Select-Object -ExpandProperty fDenyTSConnections"
        result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
        rdp_status = int(result.stdout.strip())
        if rdp_status == 0:
            print("RDP is enabled.")
        else:
            print("RDP is disabled.")
        return rdp_status == 0
    except subprocess.CalledProcessError as e:
        print(f"Error checking RDP status: {e}")
        print(f"Error output: {e.stderr}")
        return None

# Enable RDP and set the network profile to Private if necessary
def enable_rdp():
    print("Checking network profile and RDP status...")

    # Check current network profile
    current_profile = get_network_category()
    if current_profile != "Private":
        print(f"Current network profile is '{current_profile}'. Changing to Private...")
        if not change_network_to_private():
            print("Failed to change network profile to Private. RDP may not be enabled correctly.")
            return False
    else:
        print("Network profile is already set to Private.")

    # Check if RDP is already enabled
    rdp_status = check_rdp_status()
    if rdp_status is True:
        print("RDP is already enabled.")
        return True
    elif rdp_status is None:
        print("Unable to determine RDP status. Proceeding with enable process.")
    else:
        print("RDP is currently disabled. Enabling RDP...")

    # Commands to enable RDP
    commands = [
        ("Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'", "Error enabling firewall rules"),
        (r"Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\Terminal Server' -Name 'fDenyTSConnections' -Value 0", "Error setting RDP properties"),
        ("Restart-Service -Name 'TermService' -Force", "Error restarting RDP service")
    ]

    try:
        for command, error_message in commands:
            result = subprocess.run(["powershell", "-Command", command], capture_output=True, text=True, check=True)
            print(f"Successfully executed: {command}")
            print(f"Output: {result.stdout}")

        # Verify RDP is enabled after the process
        if check_rdp_status():
            print("RDP enabled successfully.")
            return True
        else:
            print("RDP enabling process completed, but final status check failed.")
            return False
    except subprocess.CalledProcessError as e:
        print(f"Error: {error_message}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"Exception occurred while enabling RDP: {e}")
        return False

# Discover server on the network via UDP broadcast
def discover_server(port=12345):
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    udp_socket.settimeout(5)

    try:
        udp_socket.sendto(b"DISCOVER_SERVER", ('<broadcast>', port))
        print("Broadcasted discovery message.")
        try:
            response, addr = udp_socket.recvfrom(1024)
            if response == b"SERVER_HERE":
                return addr[0]
        except socket.timeout:
            print("No server response received.")
    except socket.error as e:
        print(f"UDP socket error: {e}")
    finally:
        udp_socket.close()

    return None

# Connect to the discovered server
def connect_to_server(server_ip, port=12345):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client_socket.connect((server_ip, port))
        hostname = socket.gethostname()
        print(f"Sending hostname: {hostname}")
        client_socket.sendall(f"HOSTNAME {hostname}".encode())
        return client_socket
    except (socket.timeout, socket.error) as e:
        print(f"Failed to connect to server: {e}")
        client_socket.close()
        return None

# Handle file paths for installation
def handle_file_path(file_path):
    print(f"Handling file path: {file_path}")

# Install software using Winget
def install_software(file_path):
    try:
        print(f"Installing software from path: {file_path}")
        result = subprocess.run(["winget", "install", file_path], capture_output=True, text=True, check=True)
        if result.returncode == 0:
            print(f"Installation succeeded: {result.stdout}")
        else:
            print(f"Installation failed with exit code {result.returncode}")
            print(f"Error output: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Installation command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except Exception as e:
        print(f"Exception occurred while installing software: {e}")

# Download software from server and install
def download_and_install_software(server_ip, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as tcp_socket:
            tcp_socket.connect((server_ip, port))
            tcp_socket.sendall(b"UPLOAD")
            file_name = tcp_socket.recv(1024).decode()
            file_path = os.path.join(os.path.expanduser("~"), file_name)
            with open(file_path, "wb") as f:
                while True:
                    data = tcp_socket.recv(4096)
                    if data == b"END_OF_FILE":
                        break
                    f.write(data)
            print(f"File downloaded and saved to {file_path}")
            install_software(file_path)
    except Exception as e:
        print(f"Error downloading and installing software: {e}")

def main_client():
    port = 12345
    client_socket = None
    local_hostname = get_local_hostname()

    # Set up signal handling for graceful exit
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


    while True:
        if client_socket is None:
            print("Searching for server...")
            server_ip = discover_server(port)
            if server_ip:
                print(f"Found server at {server_ip}.")
                client_socket = connect_to_server(server_ip, port)

                if client_socket:  # Ensure connection was successful
                    # Receive the server's hostname from the first message
                    server_hostname = client_socket.recv(1024).decode().split(" ")[1]

                    # Skip connecting if the server hostname is the same as the local hostname
                    if server_hostname == local_hostname:
                        print("Detected server is on the same machine. Skipping connection.")
                        client_socket.close()
                        client_socket = None
                    else:
                        print(f"Connected to server at {server_ip}.")
            else:
                print("Retrying in 5 seconds...")
                time.sleep(5)
        else:
            try:
                print("Waiting for file path from server...")
                response = client_socket.recv(1024).decode()
                if response.startswith("FILE_PATH"):
                    file_path = response.split(" ")[1]
                    handle_file_path(file_path)
                elif response == "CLOSE":
                    client_socket.close()
                    client_socket = None
                    print("Server closed the connection. Searching for server again...")
                else:
                    print(f"Received unexpected response: {response}")
            except ConnectionResetError:
                print("Connection to server was forcibly closed. Reconnecting...")
                client_socket.close()
                client_socket = None
            except socket.error as e:
                print(f"Socket error: {e}. Reconnecting...")
                client_socket.close()
                client_socket = None
            except Exception as e:
                print(f"Unexpected error: {e}. Reconnecting...")
                client_socket.close()
                client_socket = None

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        if is_server_running():
            print("An existing server instance is already running.")
            print("Elevating to server mode.")
            # Additional logic for elevating to server can go here
        else:
            print("Starting server...")
            server = Server()
            sys.exit(app.exec_())
    else:
        print("Starting as client...")
        enable_rdp()
        main_client()
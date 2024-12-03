from PyQt5 import QtWidgets, QtCore, QtGui
import threading
import subprocess
import socket
import os

from osfmbinaries.utils import show_toast_notification
host = subprocess.getoutput("hostname")
class Server(QtWidgets.QMainWindow):
    def __init__(self, host="0.0.0.0", port=12345):
        super().__init__()
        self.server_ip = host
        self.server_port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        self.connections = {}
        self.network_share_path = r"\\NETWORK_SHARE\path\to\folder"  # Replace if needed
        self.setup_ui()
        self.start_udp_listener()
        self.start_tcp_server()
        self.apply_styling()  # Apply styling at the end

    def enable_internet(self):
        command = "Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ResetServerAddresses"
        self.send_command(f"POWERSHELL {command}")

    def disable_internet(self):
        command = "Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ServerAddresses '0.0.0.0'"
        self.send_command(f"POWERSHELL {command}")

    def create_user(self):
        username = QtWidgets.QInputDialog.getText(self, "Create User", "Enter username:")
        if username[1]:
            password = QtWidgets.QInputDialog.getText(self, "Create User", "Enter password:", QtWidgets.QLineEdit.Password)
            if password[1]:
                # Command to create a user and add to Administrators group
                command = (
                    f"net user {username[0]} {password[0]} /add ; "
                    f"net localgroup Administrators {username[0]} /add"
                )
                self.send_command(f"POWERSHELL {command}")
                self.send_command(f"TOASTC {username[0]}")
                show_toast_notification("User Management",f"User {username[0]} Created")

    def delete_user(self):
        username = QtWidgets.QInputDialog.getText(self, "Delete User", "Enter username to delete:")
        if username[1]:
            # Command to delete the user
            command = f"net user {username[0]} /delete"
            self.send_command(f"POWERSHELL {command}")
            self.send_command(f"TOASTD {username[0]}")
            show_toast_notification("User Management",f"User {username[0]} Deleted")

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

        # Create buttons for enabling/disabling internet
        self.enable_button = QtWidgets.QPushButton('Enable Internet', self)
        self.enable_button.clicked.connect(self.enable_internet)

        self.disable_button = QtWidgets.QPushButton('Disable Internet', self)
        self.disable_button.clicked.connect(self.disable_internet)

        # Add buttons to layout
        button_layout.addWidget(self.enable_button)
        button_layout.addWidget(self.disable_button)

        # Create buttons for user management
        self.create_user_button = QtWidgets.QPushButton('Create User', self)
        self.create_user_button.clicked.connect(self.create_user)

        self.delete_user_button = QtWidgets.QPushButton('Delete User', self)
        self.delete_user_button.clicked.connect(self.delete_user)

        # Add user management buttons to layout
        button_layout.addWidget(self.create_user_button)
        button_layout.addWidget(self.delete_user_button)

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
                self.send_command(host) # Sends the server hostname on connection
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
                if data.startswith(b"UPLOAD"):  # Likely not used, but kept for completeness if you need file uploads
                    self.receive_file(client_socket)
                elif data.startswith(b"FILE_PATH"):  # NOT USED CURRENTLY
                    file_path = data.decode().split(" ", 1)[1]
                    self.handle_file_path(file_path)  # Potentially for future use
                elif data.startswith(b"UNINSTALL"): # NOT USED CURRENTLY
                    software_id = data.decode().split(" ", 1)[1]
                    self.uninstall_software(software_id) # If implementing a software list
            except Exception as e:
                print(f"Client connection error: {e}")
                break
        client_socket.close()
        if hostname in self.connections:
            del self.connections[hostname]
        self.update_clients_list()

    def receive_file(self, client_socket): # Likely redundant
        try:
            file_name = client_socket.recv(1024).decode()
            file_path = os.path.join(self.network_share_path, file_name) # Or some other save location

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



    def send_command(self, command):
        for conn in self.connections.values():
            try:
                conn.sendall(command.encode())
            except Exception as e:
                print(f"Failed to send command: {e}")

    def install_software(file_path):
        if os.path.isdir(file_path):
            files = os.listdir(file_path)
            executables = [f for f in files if f.endswith(('.exe', '.msi'))]
            if not executables:
                print("No executable files found in the directory.")
                return
            for executable in executables:
                full_path = os.path.join(file_path, executable)
                print(f"Installing {full_path}...")
                # Use Start-Process to execute the installer with the UNC path
                command = f'cmd.exe /c "{full_path}" /quiet'
                print(command)
                subprocess.run(command)
        else:
            print(f"The path is not a directory: {file_path}")


    def uninstall_software(self, software_id=None):  # Takes software_id as an argument now
        if not software_id:  # If no ID provided, prompt for input
            software_id = QtWidgets.QInputDialog.getText(self, "Uninstall Software", "Enter Software ID to uninstall:")
            if not software_id[1]: # User hit cancel
                return
            software_id = software_id[0]

        command = f"winget uninstall --id \"{software_id}\"" # Quotes around app id
        self.send_command(f"POWERSHELL {command}")


    def fix_windows(self):
        self.send_command(f"FIX")
        

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
            print("Software options:", self.software_options) #Debugging line
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
            if source_pos:  # winget output changes, this adapts
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
            item.setData(QtCore.Qt.UserRole, self.software_options[name])    # Store the ID, not just the name


    def toggle_selection(self, item): # Simplified Selection
        software_id = item.data(QtCore.Qt.UserRole)    # Use item.data to get ID
        if software_id in self.selected_software:
            self.selected_software.remove(software_id)
            item.setCheckState(QtCore.Qt.Unchecked)         # Update the checkbox visually
        else:
            self.selected_software.add(software_id)
            item.setCheckState(QtCore.Qt.Checked)    # Update the checkbox visually

    def install_selected_software(self):  # Simplified Install

        for software_id in self.selected_software:

            self.download_software(software_id)
            for hostname in self.connections:
                self.send_download_path(software_id, host, hostname)
        self.send_command("INSTALL") # The "INSTALL" command is now sent

    def download_software(self, pkg_id):
        print(f"Downloading software: {pkg_id}")
        download_path = f"osfm-temp/{pkg_id}"
        result = subprocess.run(["winget", "download", "--id", pkg_id, "-d", download_path], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"Failed to download {pkg_id}: {result.stderr}")
        else:
            print(f"Successfully downloaded {pkg_id}")


    def send_download_path(self, pkg_id, host, hostname):
        file_path = self.find_downloaded_file(pkg_id)
        if file_path:
            # CRITICAL: Added "osfm-temp" share name here
            formatted_path = f"\\{host}\\osfm-temp\\{file_path}"
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

        package_dir = os.path.join("osfm-temp", pkg_id)
        if os.path.exists(package_dir):
        # Using os.walk to find files recursively (winget sometimes uses subdirs)
            for root, _, files in os.walk(package_dir): 
                for file in files:
                    if file.endswith(".exe") or file.endswith(".msi"):
                        return os.path.join(root, file)
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
        #self.software_buttons_frame.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection) ## Not needed

        self.software_buttons_frame.itemClicked.connect(self.toggle_selection) # Changed Click to itemClicked


        layout.addWidget(self.software_buttons_frame)

        install_button = QtWidgets.QPushButton("Install Selected", install_gui)

        install_button.clicked.connect(self.install_selected_software)
        layout.addWidget(install_button)


        install_gui.setStyleSheet("QListWidget::item { border-bottom: 1px solid black; }") # Slightly better visualization



        self.selected_software = set()  # initialize here


        install_gui.exec_()




    def create_uninstall_software_gui(self):  # NEEDS ADJUSTMENT IF NOT USING WINGET IDS DIRECTLY
        uninstall_gui = QtWidgets.QDialog(self)
        uninstall_gui.setWindowTitle("Uninstall Software")
        uninstall_gui.setGeometry(100, 100, 400, 100)  # Smaller dialog

        layout = QtWidgets.QVBoxLayout(uninstall_gui)

        self.uninstall_entry = QtWidgets.QLineEdit(uninstall_gui)
        self.uninstall_entry.setPlaceholderText("Enter software ID to uninstall")
        layout.addWidget(self.uninstall_entry)

        uninstall_button = QtWidgets.QPushButton("Uninstall", uninstall_gui)
        uninstall_button.clicked.connect(self.trigger_uninstall)
        layout.addWidget(uninstall_button)

        uninstall_gui.exec_()

    def trigger_uninstall(self): #Uninstall triggered here
        software_id = self.uninstall_entry.text()

        if software_id:
            self.uninstall_software(software_id) # Calls the main uninstall with ID
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

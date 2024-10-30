import subprocess
import socket
import time
import os
import signal
import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import threading
from win10toast import ToastNotifier

# Add the binaries folder to the system path
# sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'binaries'))

#OSFM Functions
from binaries import *
from binaries.utils import is_server_running, show_toast_notification, get_local_hostname, signal_handler, ensure_temp_folder_shared
from binaries.server import Server
from binaries.clientfunc import discover_server, connect_to_server, install_software, enable_rdp
from binaries.client import main_client

host = subprocess.getoutput("hostname")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        if is_server_running():
            print("An existing server instance is already running.") 
        else:
            print("Starting server...")
            # Ensure the temp folder is shared before continuing
            ensure_temp_folder_shared()
            server = Server()
            sys.exit(app.exec_())
    else:
        print("Starting as client...")
        enable_rdp()
        main_client()
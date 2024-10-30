import subprocess
import sys
from PyQt5 import QtWidgets

#OSFM Functions
from osfmbinaries import *
from osfmbinaries.utils import is_server_running, show_toast_notification, get_local_hostname, signal_handler, ensure_temp_folder_shared
from osfmbinaries.server import Server
from osfmbinaries.clientfunc import discover_server, connect_to_server, install_software, enable_rdp
from osfmbinaries.client import main_client

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
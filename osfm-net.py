import sys
from PyQt5 import QtWidgets
import subprocess
import os

#OSFM Functions
from osfm import *
from osfm.utils import is_server_running, ensure_temp_folder_shared
from osfm.server import Server
from osfm.clientfunc import enable_rdp
from osfm.client import main_client

log_file = open('osfm-net.log', 'w')
sys.stdout = log_file

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--server':
        if is_server_running():
            print("An existing server instance is already running.") 
        else:
            print("Starting server...")
            # Ensure the temp folder is shared before continuing
            base_path = os.path.dirname(__file__)
            ensure_temp_folder_shared(base_path)
            server = Server()
            sys.exit(app.exec_())
    else:
        print("Starting as client...")
        enable_rdp()
        main_client()

log_file.close()
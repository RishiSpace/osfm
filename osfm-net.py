import sys
from PyQt5 import QtWidgets

#OSFM Functions
from osfmbinaries import *
from osfmbinaries.utils import is_server_running, ensure_temp_folder_shared
from osfmbinaries.server import Server
from osfmbinaries.clientfunc import enable_rdp
from osfmbinaries.client import main_client


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
import subprocess

class Winget:
    def __init__(self):
        pass

    def search_software(self, query):
        # Implement software search using winget
        subprocess.run(f"winget search {query}", shell=True)

    def download_software(self, software_id):
        # Implement software download using winget
        subprocess.run(f"winget install {software_id}", shell=True)

    def uninstall_software(self, software_id):
        # Implement software uninstallation using winget
        subprocess.run(f"winget uninstall {software_id}", shell=True)
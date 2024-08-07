I need Python code to create a server and client application that interact over TCP and UDP, integrate with Active Directory (AD), and handle software management with the constraint that the client has no internet access and relies on the server for all downloading. The server and client should operate as follows: 

  

Server Application 

Versioning 
The server should have a defined version label, which is "V1.03 (Net)". 
Update Checking 
The server muse have a dark themeing 
The server must periodically check for updates from a specific URL. If a new version is available that differs from the current version, it should print a message indicating the availability of an update. 
UDP Communication 
The server should listen for UDP messages on a specified port, responding to discovery requests from clients by indicating its presence. 
TCP Communication 
The server should accept TCP connections from clients. It should handle incoming connections, receive client information, and manage a list of connected clients. 
The server should send commands to clients, such as installing or uninstalling software, fixing system issues, and handling file uploads. 
Active Directory Integration 
Authentication: Utilize AD for client authentication. Verify client identities using AD credentials and manage client connections based on AD group memberships. 
File Sharing: Configure SMB file shares using AD. Share a folder for software downloads and ensure that permissions are managed through AD groups. 
Software Deployment: Use AD Group Policies to deploy software and updates to clients, simplifying software management. 
User Interface 
The server should have a GUI using PyQt5 with the following features: 
Install Software Button: Opens a new window allowing users to search for software using winget (on Windows) or apt (on Linux). Users can select software, which will be downloaded to a server-side folder using winget download or equivalent commands. This folder is then shared via SMB. 
Uninstall Software Button: Allows software to be uninstalled from clients. 

Fix Windows Button: Sends a command to clients to perform system repairs. 

Send terminal Command Button: Sends PowerShell or Bash commands to clients depending on the client's OS. 

Client List: Displays a list of connected clients with information about their hostnames and operating systems. 

  

Software Download Handling 

  

The server should handle all downloading of software. It should: 

Download selected software to a server-side folder. 

Share this folder over SMB with the clients. 

Ensure clients can access and install the software from this shared location. 

Client Application 

Versioning 

  

The client should also have a defined version label, which matches the server's version. 

Server Discovery and Connection 

  

The client should periodically broadcast a message over UDP to discover the server. Upon finding the server, it should connect using TCP and authenticate using AD credentials. 

Command Handling 

  

Upon connection, the client should send its hostname and operating system information to the server. It should handle various commands from the server, such as installing or uninstalling software, running system scans, and executing PowerShell or bash commands. 

File Handling 

  

Since the client has no internet access, it should: 

Access the SMB-shared folder on the server to retrieve downloaded setup files. 

Execute the installation commands appropriate for the client’s operating system using the files from the shared folder. 

Remote Desktop 

  

On Linux systems, if the client is instructed to enable Remote Desktop, it should use AD to manage and configure xrdp. 

Continuous Operation 

  

The client should maintain a persistent connection to the server, handling reconnections automatically in case of disconnections. 

Integration Details 

Active Directory Integration 

  

AD Authentication: Use libraries or system commands to authenticate clients against AD. 

Shared Folders: Configure SMB shares using AD permissions to ensure secure access to the shared software download folder. 

Group Policy: Leverage AD Group Policies for software deployment and updates. 

Error Handling and Security 

  

Implement robust error handling for network issues, authentication failures, and file operations. Ensure that all interactions are secure and comply with best practices for AD integration. 

 

 

 import os
import subprocess

def find_and_install_files(root_folder):
    # Define the file extensions to search for
    file_extensions = ('.exe', '.msi')

    # Walk through the directory
    for root, dirs, files in os.walk(root_folder):
        for file in files:
            # Check if the file has one of the specified extensions
            if file.lower().endswith(file_extensions):
                file_path = os.path.join(root, file)
                print(f"Found installer: {file_path}")
                try:
                    # Install the file
                    # Note: Ensure you have the necessary permissions
                    subprocess.run([file_path], check=True)
                    print(f"Successfully installed: {file_path}")
                except subprocess.CalledProcessError as e:
                    print(f"Failed to install {file_path}. Error: {e}")

if __name__ == "__main__":
    # Replace this path with your network folder path
    network_folder_path = r'\\network\path\to\folder'
    find_and_install_files(network_folder_path)


# Compile
pyinstaller --onefile final_server.py --name server ; pyinstaller --onefile final_client.py --name client
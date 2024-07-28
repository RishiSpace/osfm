#include <iostream>
#include <cstdlib>
#include <string>
using namespace std;

void install_program(const string& distro, const string& package_manager, const string& package) {
    string command = "sudo " + package_manager + " install " + package;
    cout << "Installing " << package << ", please enter your password if prompted\n";
    system(command.c_str());
}

void install_custom_program(const string& package_manager) {
    string program;
    cout << "Enter the name of the program you want to install: ";
    cin >> program;
    install_program("", package_manager, program);
}

int Linux() {
    int l, lp;
    cout << "We've detected that you are using Linux, could you please specify which Distribution of Linux you are using?\n\n";
    cout << "1. Debian (Ubuntu, PopOs, Mint, ZorinOS)\n";
    cout << "2. Arch Linux (Manjaro, Garuda)\n";
    cout << "3. Fedora\n\n";
    cout << "Enter your choice (Number only): ";
    cin >> l;

    if (l < 1 || l > 3) {
        cout << "Sorry, wrong choice\n";
        return 1;
    }

    cout << "\nWhich program do you want to install?\n\n";
    cout << "1. Firefox\n";
    cout << "2. Neofetch\n";
    cout << "3. Terminator\n";
    cout << "4. Spotify\n";
    cout << "5. Chrome\n";
    cout << "6. VSCode\n";
    cout << "7. Steam\n";
    cout << "8. Lutris\n";
    cout << "9. Brave\n";
    cout << "10. VLC Media Player\n";
    cout << "11. Custom (Enter name of the program)\n";
    cout << "0. All of the above\n\n";
    cout << "Enter your choice (Number only): ";
    cin >> lp;

    string package_manager;
    if (l == 1) package_manager = "apt";
    else if (l == 2) package_manager = "pacman -S";
    else if (l == 3) package_manager = "dnf";

    switch (lp) {
        case 1: install_program("", package_manager, "firefox"); break;
        case 2: install_program("", package_manager, "neofetch"); break;
        case 3: install_program("", package_manager, "terminator"); break;
        case 4: 
            if (l == 1) {
                system("sudo apt install snap && sudo snap install spotify");
            } else if (l == 2) {
                system("yay -S spotify");
            } else if (l == 3) {
                system("flatpak install com.spotify.Client");
            }
            break;
        case 5: 
            if (l == 1) {
                system("sudo apt install snap && sudo snap install chrome");
            } else if (l == 2) {
                system("yay -S google-chrome");
            } else if (l == 3) {
                system("flatpak install com.google.Chrome");
            }
            break;
        case 6: 
            if (l == 1) {
                system("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg");
                system("sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/");
                system("sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'");
                system("rm -f packages.microsoft.gpg");
                system("sudo apt install apt-transport-https && sudo apt update && sudo apt install code");
            } else if (l == 2) {
                system("yay -S visual-studio-code-bin");
            } else if (l == 3) {
                system("flatpak install com.visualstudio.code");
            }
            break;
        case 7: install_program("", package_manager, "steam"); break;
        case 8: install_program("", package_manager, "lutris"); break;
        case 9: 
            if (l == 1) {
                system("sudo apt install apt-transport-https curl");
                system("sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg");
                system("echo \"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main\" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list");
                system("sudo apt update");
                system("sudo apt install brave-browser");
            } else if (l == 2) {
                system("yay -S brave-bin");
            } else if (l == 3) {
                system("flatpak install com.brave.Browser");
            }
            break;
        case 10: install_program("", package_manager, "vlc"); break;
        case 11: install_custom_program(package_manager); break;
        case 0: 
            install_program("", package_manager, "firefox");
            install_program("", package_manager, "neofetch");
            install_program("", package_manager, "terminator");
            if (l == 1) {
                system("sudo apt install snap && sudo snap install spotify");
                system("sudo apt install snap && sudo snap install chrome");
            } else if (l == 2) {
                system("yay -S spotify");
                system("yay -S google-chrome");
            } else if (l == 3) {
                system("flatpak install com.spotify.Client");
                system("flatpak install com.google.Chrome");
            }
            if (l == 1) {
                system("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg");
                system("sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/");
                system("sudo sh -c 'echo \"deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] https://packages.microsoft.com/repos/code stable main\" > /etc/apt/sources.list.d/vscode.list'");
                system("rm -f packages.microsoft.gpg");
                system("sudo apt install apt-transport-https && sudo apt update && sudo apt install code");
            } else if (l == 2) {
                system("yay -S visual-studio-code-bin");
            } else if (l == 3) {
                system("flatpak install com.visualstudio.code");
            }
            install_program("", package_manager, "steam");
            install_program("", package_manager, "lutris");
            if (l == 1) {
                system("sudo apt install apt-transport-https curl");
                system("sudo curl -fsSLo /usr/share/keyrings/brave-browser-archive-keyring.gpg https://brave-browser-apt-release.s3.brave.com/brave-browser-archive-keyring.gpg");
                system("echo \"deb [signed-by=/usr/share/keyrings/brave-browser-archive-keyring.gpg arch=amd64] https://brave-browser-apt-release.s3.brave.com/ stable main\" | sudo tee /etc/apt/sources.list.d/brave-browser-release.list");
                system("sudo apt update");
                system("sudo apt install brave-browser");
            } else if (l == 2) {
                system("yay -S brave-bin");
            } else if (l == 3) {
                system("flatpak install com.brave.Browser");
            }
            install_program("", package_manager, "vlc");
            break;
        default: cout << "Sorry, wrong input\n"; break;
    }
    return 0;
}

int Windows() {
    system("color 3");
    int w, wp;
    cout << "We've detected that you're using Windows. Could you please specify the version of Windows that you are using?\n\n";
    cout << "1. Windows 10\n";
    cout << "2. Windows 10 with Winget\n";
    cout << "3. Windows 11\n";
    cout << "\nTip: if you don't know if you have winget installed or not, launch a cmd instance and type 'winget --help'. If you see errors, then winget is not installed.\n";
    cin >> w;

    if (w < 1 || w > 3) {
        cout << "Sorry, wrong choice\n";
        return 1;
    }

    cout << "\nWhich program do you want to install?\n\n";
    cout << "1. Firefox\n";
    cout << "2. Neofetch\n";
    cout << "3. Terminator\n";
    cout << "4. Spotify\n";
    cout << "5. Chrome\n";
    cout << "6. VSCode\n";
    cout << "7. Steam\n";
    cout << "8. Lutris\n";
    cout << "9. Brave\n";
    cout << "10. VLC Media Player\n";
    cout << "11. Custom (Enter name of the program)\n";
    cout << "0. All of the above\n\n";
    cout << "Enter your choice (Number only): ";
    cin >> wp;

    if (w == 1) {
        cout << "You need to install winget for this script to work. Install it from here: https://github.com/microsoft/winget-cli/releases\n";
        return 1;
    }

    string command = "winget install --id=";
    switch (wp) {
        case 1: system((command + "Mozilla.Firefox").c_str()); break;
        case 2: cout << "Neofetch is not available on Windows\n"; break;
        case 3: cout << "Terminator is not available on Windows\n"; break;
        case 4: system((command + "Spotify.Spotify").c_str()); break;
        case 5: system((command + "Google.Chrome").c_str()); break;
        case 6: system((command + "Microsoft.VisualStudioCode").c_str()); break;
        case 7: system((command + "Valve.Steam").c_str()); break;
        case 8: cout << "Lutris is not available on Windows\n"; break;
        case 9: system((command + "Brave.Brave").c_str()); break;
        case 10: system((command + "VideoLAN.VLC").c_str()); break;
        case 11: {
            string program;
            cout << "Enter the name of the program you want to install: ";
            cin >> program;
            system(("winget install --id=" + program).c_str());
            break;
        }
        case 0: {
            system((command + "Mozilla.Firefox").c_str());
            system((command + "Spotify.Spotify").c_str());
            system((command + "Google.Chrome").c_str());
            system((command + "Microsoft.VisualStudioCode").c_str());
            system((command + "Valve.Steam").c_str());
            system((command + "Brave.Brave").c_str());
            system((command + "VideoLAN.VLC").c_str());
            break;
        }
        default: cout << "Sorry, wrong input\n"; break;
    }
    return 0;
}

int main() {
    string OS;
    cout << "Enter the Operating System you are using (Linux/Windows): ";
    cin >> OS;

    if (OS == "Linux" || OS == "linux") {
        Linux();
    } else if (OS == "Windows" || OS == "windows") {
        Windows();
    } else {
        cout << "Sorry, wrong choice\n";
    }

    return 0;
}

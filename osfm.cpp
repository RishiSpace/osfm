#include<iostream>
#include<stdio.h>
#include<math.h>
using namespace std;
int main()
{
    printf ("Hello welcome to osfm, a program made by Rishi Space\n");
    while (true)
    {
        int i,os;
        #ifdef linux
        {
            os = 1;
        }
        #else
        {
            os = 2;
        }
        #endif
        printf("1.Install Programs\n");
        printf("0. Exit Program\n\n");
        printf("enter the feature you wanna use: ");
        scanf("%d",&i);
        if (i == 1)
        {
            if (os == 1)
            {
                char l,lp;
                printf("We've detected that you are using Linux, could you please specify which Distribution of Linux you are using ?\n");
                printf("1. Debian (Ubuntu, PopOs, Mint, ZorinOS)\n");
                printf("2. Arch Linux (Manjaro, Garuda)\n");
                printf("3. Fedora\n");
                scanf("%d",&l);
                printf("Which program do you wanna install ? \n");
                printf("1. Firefox\n");
                printf("2. Neofetch\n");
                printf("3. terminator\n");
                printf("4. spotify\n");
                printf("5. chrome\n");
                printf("6. vscode\n");
                printf("7. Steam\n");
                printf("8. Lutris\n");
                printf("0. All of the above\n");
                scanf ("%d",&lp);
                if (l == 1)
                {
                    if (lp == 1)
                    {
                        //Firefox
                        printf("Installing Firefox, please enter your password if prompted\n");
                        system ("sudo apt install firefox");
                    }
                    else if (lp == 2)
                    {
                        //Neofetch
                        printf("Installing neofetch, please enter your password if prompted\n");
                        system ("sudo apt install neofetch");
                    }
                    else if (lp == 3)
                    {
                        //Terminator
                        printf("Installing Terminator, please enter your password if prompted\n");
                        system ("sudo apt install terminator");
                    }
                    else if (lp == 4)
                    {
                        //spotify
                        printf("Installing Spotify, please enter your password if prompted\n");
                        system ("sudo apt install snap && sudo snap install spotify");
                    }
                    else if (lp == 5)
                    {
                        //chrome
                        printf("Installing Chrome, please enter your password if prompted\n");
                        system ("sudo apt install snap && sudo snap install chrome");
                    }
                    else if (lp == 6)
                    {
                        //vscode
                        printf("Installing vscode, please enter your passowrd if prompted\n");
                        system ("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg");
                        system ("sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/");
                        system ("sudo sh -c 'echo 'deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] 'https://packages.microsoft.com/repos/code stable main' > '/etc/apt/sources.list.d/vscode.list'");
                        system ("rm -f packages.microsoft.gpg");
                        system ("sudo apt install apt-transport-https && sudo apt update && sudo apt install code");
                    }
                    else if (lp == 7)
                    {
                        //steam
                        printf("Installing Steam, please enter your passowrd if prompted\n");
                        system ("sudo apt install steam");
                    }
                    else if (lp == 8)
                    {
                        //lutris
                        printf("Installing Lutris, please enter your passowrd if prompted\n");
                        system ("sudo apt install lutris");
                    }
                    else if (lp == 0)
                    {
                        //All of the above
                        printf("Installing all programs mentioned above (This may take some time), please enter your password if prompted\n");
                        system ("sudo apt install firefox");
                        system ("sudo apt install neofetch");
                        system ("sudo apt install terminator");
                        system ("sudo apt install snap && sudo snap install spotify");
                        system ("sudo apt install snap && sudo snap install chrome");
                        system ("wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > packages.microsoft.gpg");
                        system ("sudo install -o root -g root -m 644 packages.microsoft.gpg /etc/apt/trusted.gpg.d/");
                        system ("sudo sh -c 'echo 'deb [arch=amd64,arm64,armhf signed-by=/etc/apt/trusted.gpg.d/packages.microsoft.gpg] 'https://packages.microsoft.com/repos/code stable main' > '/etc/apt/sources.list.d/vscode.list'");
                        system ("rm -f packages.microsoft.gpg");
                        system ("sudo apt install apt-transport-https && sudo apt update && sudo apt install code");
                        system ("sudo apt install steam");
                        system ("sudo apt install lutris");
                    }
                    else
                    {
                        printf("sorry wrong input");
                    }
                }
                else if (l == 2)
                {
                    //prerequisites
                    printf("Hang on, we're making sure you can install the programs, please enter your password if prompted");
                    system ("sudo pacman -S yay");
                    if (lp == 1)
                    {
                        //Firefox
                        printf("Installing Firefox, please enter your password if prompted\n");
                        system ("sudo pacman -s firefox");
                    }
                    else if (lp == 2)
                    {
                        //Neofetch
                        printf("Installing Neofetch, please enter your password if prompted\n");
                        system ("sudo pacman -S neofetch");
                    }
                    else if (lp == 3)
                    {
                        //terminator
                        printf("Installing teminator, please enter your password if prompted\n");
                        system ("sudo pacman -S terminator");
                    }
                    else if (lp == 4)
                    {
                        //spotify
                        printf("Installing spotify, please enter your password if prompted\n");
                        system ("yay -S spotify");
                    }
                    else if (lp == 5)
                    {
                        //chrome
                        printf("Installing chrome, please enter your password if prompted\n");
                        system ("yay -S chrome");
                    }
                    else if (lp == 6)
                    {
                        //vscode
                        printf("Installing vscode, please enter your password if prompted\n");
                        system ("yay -S vscode");
                    }
                    else if (lp == 7)
                    {
                        //steam
                        printf("Installing Steam, please enter your passowrd if prompted\n");
                        system ("yay -S steam");
                    }
                    else if (lp == 8)
                    {
                        //lutris
                        printf("Installing Lutris, please enter your passowrd if prompted\n");
                        system ("yay -S lutris");
                    }
                    else if (lp == 0)
                    {
                        //All of the above
                        printf("Installing all programs mentioned above (This may take some time), please enter your password if prompted\n");
                        system ("sudo pacman -s firefox");
                        system ("sudo pacman -S neofetch");
                        system ("sudo pacman -S terminator");
                        system ("yay -S spotify");
                        system ("yay -S chrome");
                        system ("yay -S vscode");
                        system ("yay -S steam");
                        system ("yay -S lutris");
                    }
                    else
                    {
                        printf("oops wrong choice");
                    }
                }
                else if (l == 3)
                {
                    //prerequisites
                    printf ("Please wait while we check if we can install programs on this system. Enter your password if prompted");
                    system ("sudo dnf install flatpak");
                    if (lp == 1)
                    {
                        //Firefox
                        printf("Installing Firefox, please enter your password if prompted\n");
                        system ("sudo dnf install firefox");
                    }
                    else if (lp == 2)
                    {
                        //Neofetch
                        printf("Installing Neofetch, please enter your password if prompted\n");
                        system ("sudo dnf install neofetch");
                    }
                    else if (lp == 3)
                    {
                        //terminator
                        printf("Installing teminator, please enter your password if prompted\n");
                        system ("sudo dnf install terminator");
                    }
                    else if (lp == 4)
                    {
                        //spotify
                        printf("Installing spotify, please enter your password if prompted\n");
                        system ("flatpak install com.spotify.Client");
                    }
                    else if (lp == 5)
                    {
                        //chrome
                        printf("Installing chrome, please enter your password if prompted\n");
                        system ("flatpak install com.google.Chrome");
                    }
                    else if (lp == 6)
                    {
                        //vscode
                        printf("Installing vscode, please enter your password if prompted\n");
                        system ("flatpak install com.visualstudio.code");
                    }
                    else if (lp == 7)
                    {
                        //steam
                        printf("Installing Steam, please enter your passowrd if prompted\n");
                        system ("sudo dnf install steam");
                    }
                    else if (lp == 8)
                    {
                        //lutris
                        printf("Installing Lutris, please enter your passowrd if prompted\n");
                        system ("sudo dnf install lutris");
                    }
                    else if (lp == 0)
                    {
                        //All of the above
                        printf("Installing all programs mentioned above (This may take some time), please enter your password if prompted\n");
                        system ("sudo dnf install firefox");
                        system ("sudo dnf install neofetch");
                        system ("sudo dnf install terminator");
                        system ("flatpak install com.spotify.Client");
                        system ("flatpak install com.google.Chrome");
                        system ("flatpak install com.visualstudio.code");
                        system ("sudo dnf install steam");
                        system ("sudo dnf install lutris");
                    }
                    else
                    {
                        printf("oops wrong choice");
                    }
                }
                else
                {
                    printf ("sorry wrong Choice");
                }
            }
            if (os == 2)
            {
                int w,wp;
                printf ("We've detected that you're using Windows. Could you please specify the version of windows that you are using ? \n");
                printf ("1. windows 10\n");
                printf ("2. Windows 10 with Winget\n");
                printf ("3. Windows 11\n");
                scanf("%d",&w);
                printf("Which program do you wanna install ? \n");
                printf("1. Firefox\n");
                printf("2. notepad++\n");
                printf("3. vscode\n");
                printf("4. spotify\n");
                printf("5. chrome\n");
                printf("6. Discord\n");
                printf("7. steam\n");
                printf("8. Epic Games Launcher\n");
                printf("9. OBS Studio\n");
                printf("0. All of the above\n");
                scanf("%d",&wp);
                if (w == 1)
                {
                    printf("sorry our program doesn't work without winget yet. Please install winget by updating App Installer or upgrade to Windows 11 if possible :)");
                }
                else if (w == 2)
                {
                    if (wp == 1)
                    {
                        //Firefox
                        printf("Installing Firefox, please enter your password if prompted\n");
                        system ("winget install Mozilla.Firefox -e");
                    }
                    else if (wp == 2)
                    {
                        //notepad++
                        printf("Installing Notepad++, please enter your password if prompted\n");
                        system ("winget install Notepad++.Notepad++ -e");
                    }
                    else if (wp == 3)
                    {
                        //vscode
                        printf("Installing vscode, please enter your password if prompted\n");
                        system ("winget install Microsoft.VisualStudioCode -e");
                    }
                    else if (wp == 4)
                    {
                        //spotify
                        printf("Installing spotify, please enter your password if prompted\n");
                        system ("winget install Spotify.Spotify -e");
                    }
                    else if (wp == 5)
                    {
                        //chrome
                        printf("Installing chrome, please enter your password if prompted\n");
                        system ("winget install Google.Chrome -e");
                    }
                    else if (wp == 6)
                    {
                        //discord
                        printf("Installing Discord, please enter your password if prompted\n");
                        system ("winget install Discord.Discord -e");
                    }
                    else if (wp == 7)
                    {
                        //steam
                        printf("Installing Steam, please enter your password if prompted\n");
                        system ("winget install Valve.Steam -e");
                    }
                    else if (wp == 8)
                    {
                        //Epic games Launcher
                        printf("Installing Epic games Launcher, please enter your password if prompted\n");
                        system ("winget install EpicGames.EpicGamesLauncher -e");
                    }
                    else if (wp == 9)
                    {
                        //OBS Studio
                        printf("Installing OBS Studio, please enter your password if prompted\n");
                        system ("winget install OBSProject.OBSStudio -e");
                    }
                    else if (wp == 0)
                    {
                        //All of the above
                        printf("Installing All of the above programs (this may take some time), please enter your password if prompted\n");
                        system ("winget install Mozilla.Firefox -e");
                        system ("winget install Notepad++.Notepad++ -e");
                        system ("winget install Microsoft.VisualStudioCode -e");
                        system ("winget install Spotify.Spotify -e");
                        system ("winget install Google.Chrome -e");
                        system ("winget install Discord.Discord -e");
                        system ("winget install Valve.Steam -e");
                        system ("winget install EpicGames.EpicGamesLauncher -e");
                        system ("winget install OBSProject.OBSStudio -e");
                    }
                    else
                    {
                        printf("oops wrong choice");
                    }
                }
            }
            else
            {
                printf ("sorry wrong choice");
            }
        }
        else if (i == 0)
        {
            // Quit Program
            printf("\n");
            exit (0);
            break;
        }
        else
        {
            // Try Again
            printf("Oops Wrong choice, try again");
        }
    }
    return 0;
}

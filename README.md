# OSFM Net — WinUI 3 Native (Windows 11, C++)

Extension of OSFM that lets administrators perform OSFM functions network-wide —
now a **Windows-native WinUI 3 (C++/WinRT)** app with proper privileged access.
This branch (`osfm-winui`) contains **only** the native rewrite; the legacy
Python/PyQt prototype was removed (see git history for `osfmbinaries/`).

## Download (no build needed)

- Head over to the **Releases** tab → latest `v*` (or rolling `winui-latest` pre-release)
- Download **`osfm-server.exe`** and **`osfm-client.exe`** (+ `SHA256SUMS.txt` to verify)
- Launch `osfm-server.exe` on the admin box; launch `osfm-client.exe` **as Administrator**
  on every machine to control (client auto-discovers the server via UDP broadcast —
  no IP entry needed)
- Whatever you trigger from the Control Centre (install/uninstall, Fix Windows,
  PowerShell, internet on/off/share, create/delete user, RDP) executes on all clients

## Build from source (Windows)

- VS 2022 17.8+, Windows App SDK 1.5+, C++/WinRT, SDK 10.0.22621+
- Open `winui/OSFM-Net.sln` → NuGet restores automatically → `Release|x64`
- Or push a `v*` tag: `.github/workflows/winui-build.yml` compiles on
  `windows-latest` and attaches both EXEs to the Release

## Layout

- `winui/Common/` — `OsfmCore.lib` (protocol, Winsock, elevation/SMB/firewall/RDP, winget, toasts, log)
- `winui/Server/ServerApp/` — Control Centre (highestAvailable manifest)
- `winui/Client/ClientApp/` — agent (requireAdministrator manifest)
- `winui/Installer/` — firewall/SMB scripts + MSIX/GPO notes
- `winui/docs/` — PLAN, PROTOCOL (wire format), SECURITY (privilege model)

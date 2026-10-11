# OSFM-Net — WinUI 3 (Windows 11) Native Overhaul (C++/WinRT)

Windows-native, privileged rewrite of the Python/PyQt `osfm-net` prototype.
Two WinAppSDK / WinUI 3 apps in C++ share one core library:

```
winui/
  Common/                 OsfmCore static lib (protocol, sockets, winget, privilege, toast, log)
  Server/ServerApp/       OSFM Control Centre (WinUI 3 window, TCP+UDP server)
  Client/ClientApp/       OSFM Client agent (WinUI 3 minimal UI + background engine, requires admin)
  Installer/              MSIX manifests, elevation manifests, setup scripts
  docs/                   protocol + privilege notes
```

## Feature parity with the Python version

| Python (`osfm-net-onefile.py` / `osfmbinaries/`) | WinUI 3 C++ port |
|---|---|
| UDP `DISCOVER_SERVER` → `SERVER_HERE` on 12345 | `UdpDiscoveryResponder` (server) + `DiscoverServer()` (client) in `OsfmCore` |
| TCP server, `HOSTNAME <pc>`, per-client threads, client list, RDP double-click (`mstsc /v:`) | `TcpServer` + `MainWindow` `ListView` |
| `POWERSHELL <cmd>`, `FILE_PATH \\host\osfm-temp\pkg`, `INSTALL`, `FIX`, `SET_DNS <ip>`, `TOASTC/D <user>`, `CLOSE`, `200 OK`/`500 ERROR` + progress bar | Identical wire protocol in `OsfmProtocol.h`; `ClientEngine::HandleCommand` |
| `winget search/download/uninstall`, `osfm-temp` SMB share (`New-SmbShare osfm-temp`) | `Winget` + `Privilege::EnsureSmbShare` (uses `NetShareAdd` → falls back to PowerShell, requires elevation) |
| Enable/Share/Disable internet (`Set-DnsClientServerAddress`), Create/Delete user (`net user`), Fix Windows (`sfc /scannow` + `DISM`), `Enable-NetFirewallRule Remote Desktop` + `fDenyTSConnections=0` | Same PowerShell, launched from elevated context via `ProcessUtils::RunElevated` |
| `win10toast`/`plyer` toasts | WinRT `ToastNotificationManager` in `Toast.h/.cpp` |
| Single-instance server check (bind 12345) | `NetUtils::IsPortInUse` + `App::OnLaunched` guard |

## Requirements (build machine must be Windows 10 1809+ / 11)

- Visual Studio 2022 17.8+ with **C++ desktop + UWP + Windows App SDK** workloads
- **Windows App SDK 1.5+** (WinUI 3), **C++/WinRT VSIX**, Windows SDK 10.0.22621+
- MSVC v143, C++20

## Build

1. Open `winui/OSFM-Net.sln` in VS 2022.
2. Restore NuGet (`Microsoft.WindowsAppSDK`, `Microsoft.Windows.CppWinRT`).
3. Set `ServerApp` **or** `ClientApp` as startup, x64 Release, run.
   - Both apps self-relaunch elevated when an operation needs admin
     (`Privilege::EnsureElevated`). For full function, **run as Administrator**.
4. Server auto-creates/shares `%ProgramData%\OSFM\osfm-temp` as `\\<HOST>\osfm-temp`.
5. To package: Packaging project → Create App Packages (sideload/MSIX). See `Installer/`.

> You are currently on Linux — this tree is authored to be opened/built on Windows.
> No Python, Qt, or `winget` parsing changes on the wire: old Python clients/servers
> interoperate with these C++ builds on port 12345.

## Privileged access design (Windows native)

- **Elevation:** `app.manifest` — Client `requireAdministrator`, Server `highestAvailable`
  + runtime `Privilege::IsElevated()` / `EnsureElevated()` (ShellExecuteEx `runas` relaunch).
- **Firewall:** server opens TCP+UDP 12345 via `netsh advfirewall` (elevated) on first start.
- **SMB share:** `NetShareAdd("osfm-temp")` with `Everyone:FULL`; fallback `New-SmbShare`.
- **RDP/client:** `EnableRdp()` sets `HKLM\...\Terminal Server\fDenyTSConnections=0`,
  enables `Remote Desktop` firewall group, sets Private profile, restarts `TermService`.
- **SFC/DISM, `net user`, DNS cmdlets:** executed through `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command`.
- **MSIX:** `runFullTrust`, `localSystemServices`-adjacent tasks documented in
  `Installer/`; for domain/AD Group Policy deployment use the unsigned MSIX + cert.

## Wire protocol (unchanged, see `docs/PROTOCOL.md`)

```
UDP broadcast  : "DISCOVER_SERVER"  ->  "SERVER_HERE"
TCP client hello: "HOSTNAME <computername>"
Server -> client: "POWERSHELL <ps>", "FILE_PATH \\HOST\osfm-temp\<pkgId>",
                  "INSTALL", "FIX", "SET_DNS <ip>",
                  "TOASTC <user>", "TOASTD <user>", "CLOSE", "<server-hostname>"
Client -> server: "200 OK" | "500 ERROR"
```

## Layout

- `Common/include/*.h` + `Common/src/*.cpp` → `OsfmCore.lib`
- `Server/ServerApp/` — `App.xaml(.h/.cpp)`, `MainWindow.xaml(.h/.cpp)`,
  `TcpServer.h/.cpp`, `ViewModels`, `Package.appxmanifest`, `app.manifest`
- `Client/ClientApp/` — `App.xaml(.h/.cpp)`, `MainWindow.xaml(.h/.cpp)`,
  `ClientEngine.h/.cpp`, `Package.appxmanifest`, `app.manifest` (requireAdmin)
- `Installer/` — MSIX notes, `EnableFirewall.ps1`, `InstallService.ps1`

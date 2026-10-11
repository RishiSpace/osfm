# OSFM-Net WinUI3 — privilege & security notes

## Elevation model
- **ServerApp** `highestAvailable`: runs unelevated for viewing; `EnsureElevated("--server")`
  relaunches via `runas` before firewall/SMB operations. Firewall rule + `osfm-temp`
  share creation REQUIRE admin — without it the server logs and serves without staging.
- **ClientApp** `requireAdministrator`: refuses unelevated execution (RDP/DNS/SFC/DISM
  and installer launches are all privileged). `MainWindow` shows relaunch notice.

## What runs elevated (audited in Logger + UI log pane)
| Op | Mechanism | Least-privilege note |
|---|---|---|
| Firewall open TCP+UDP 12345 | `netsh advfirewall` (server first start) | rule scoped to port, `privateNetworkClientServer` cap in MSIX |
| SMB share `osfm-temp` | `NetShareAdd` → fallback `New-SmbShare … -FullAccess Everyone` | staging dir only (`%ProgramData%\OSFM\osfm-temp`); share removed on uninstall |
| RDP enable (client boot) | Private profile + `fDenyTSConnections=0` + firewall group + `TermService` restart | same as Python `enable_rdp()` |
| Users/DNS/Fix/PowerShell | `powershell.exe -NoProfile -ExecutionPolicy Bypass -Command` | commands built from allow-listed inputs (see below) |
| Installers | `cmd /c "<exe>" /quiet` or `msiexec /i … /qn` | only under server-provided UNC dir |

## Input validation (trust boundary = TCP socket)
- Command dispatch is an allow-list on prefixes (`POWERSHELL`, `FILE_PATH`, `INSTALL`,
  `FIX`, `SET_DNS`, `TOASTC/D`, `CLOSE`); anything else is logged, never executed.
- `SET_DNS` arg charset `[A-Za-z0-9.:]{1,64}`; toast usernames `[A-Za-z0-9-_.$]{1,64}`.
- Passwords are NEVER logged (data_handling Restricted); `CreateUserCommand` strings
  live only in the transient broadcast — no disk persistence.
- Hostnames/IPs shown in UI are display-only; RDP target comes from the live `Clients()`
  snapshot, not from pasted text.

## Data classification
- Hostnames/IPs: Internal (shown in client list + logs, never leave the LAN).
- Passwords (create-user dialog): Restricted — held in `PasswordBox`, cleared on close,
  never written to `OSFM-*.log`.
- No telemetry, no external network: client has no internet path by design.

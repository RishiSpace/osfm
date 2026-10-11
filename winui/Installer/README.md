# OSFM-Net Installer notes (MSIX / sideload / Group Policy)

## Option A — MSIX sideload (recommended for single-lab rollout)
1. Build `Release|x64` in VS 2022 (Windows 10 1809+ SDK, WinAppSDK 1.5+).
2. Packaging project → Create App Packages → Sideloading → output `.msix`.
3. Sign with your code-sign cert (`signtool sign /fd SHA256 /a OSFM-Net.msix`).
4. Install cert to `Local Machine\Trusted People`, then `Add-AppxPackage OSFM-Net.msix`.
5. Capabilities needed: `runFullTrust`, `privateNetworkClientServer` (+`internetClient`
   on the server only for `winget download`). No `localSystemServices` — the agent is
   a user-session app, not a service.

## Option B — unpackaged EXE via Group Policy / startup script
1. Copy `ServerApp.exe` (+ `Microsoft.WindowsAppRuntime` bootstrap) to admin box,
   `ClientApp.exe` to lab machines via GPO Software Installation or logon script.
2. Run once elevated per machine with helpers:
   `powershell -ExecutionPolicy Bypass -File EnableFirewall.ps1`
   `powershell -ExecutionPolicy Bypass -File InstallService.ps1`
3. `ClientApp` self-elevates (`requireAdministrator` manifest + `runas` fallback);
   first launch enables RDP + joins discovery automatically.

## First-run checklist (both options)
- [ ] Installed/run as Administrator (client refuses otherwise)
- [ ] TCP+UDP 12345 reachable within the LAN (Private profile)
- [ ] `\\<SERVER>\osfm-temp` browsable from a client
- [ ] Clients appear in Control Centre; double-click opens `mstsc /v:`

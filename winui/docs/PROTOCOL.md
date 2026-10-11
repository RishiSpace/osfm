# OSFM-Net wire protocol (frozen for Python <-> C++ interop)

Port **12345**, UTF-8 text, one command per `recv` (no framing — legacy behavior).

## Discovery (UDP)
- Client broadcasts `DISCOVER_SERVER` to `<broadcast>:12345`
- Server replies `SERVER_HERE` (unicast). Client uses sender IP.

## Session (TCP)
1. Client connects, sends `HOSTNAME <computername>`
2. Server replies with its own hostname string; client drops the connection
   if it equals its local hostname (self-connect guard)
3. Server keeps one thread per client; UI lists `HOSTNAME`-stripped names

## Server -> client commands
| Command | Client action | Ack |
|---|---|---|
| `POWERSHELL <ps>` | `powershell -NoProfile -ExecutionPolicy Bypass -Command <ps>` | 200/500 by exit code |
| `FILE_PATH \\HOST\osfm-temp\<pkg>` | stage dir (install on `INSTALL`) | 200 if non-empty |
| `INSTALL` | run every `.exe /quiet` / `.msi /qn` recursively under staged dir | 200 if any ran |
| `FIX` | `sfc /scannow` + DISM Check/Scan/RestoreHealth | 200 if sfc+restore exit 0 |
| `SET_DNS <ip>` | `Set-DnsClientServerAddress … -ServerAddresses <ip>` (validated charset) | 200/500 |
| `TOASTC <user>` / `TOASTD <user>` | user created/deleted toast (token-validated) | 200 if token valid |
| `CLOSE` | drop connection, resume discovery | — |
| `<server-hostname>` | connect banner (not a command) | — |

## Client -> server
- `200 OK` / `500 ERROR` after each command (drives server progress bar)
- Anything else is logged, not executed (fail-closed)

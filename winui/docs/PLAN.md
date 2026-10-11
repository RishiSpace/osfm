# OSFM-Net WinUI3 Overhaul — Staged Plan (per ~/LLMG/workflow_guide.md + opt_guide.md)

## Stage 1 — OsfmCore static lib ✅ DONE / validated
Goal: protocol + sockets + privilege + winget + toast + log, wire-compatible with Python.
Inputs: osfm-net-onefile.py, osfmbinaries/*.py. Outputs: Common/include+src (7 modules).
Validation: g++ -fsyntax-only clean (SYNTAX_EXIT:0). Decision: raw Winsock, no new deps
  (Rationale: lowest LOC, no latency overhead; Consequence: Windows-only impl + Linux stubs).

## Stage 2 — ServerApp (WinUI3 + TcpServer) ← IN PROGRESS
Goal: Control Centre UI + TCP/UDP engine with 200 OK/ERROR progress tracking.
Validation: portable parts syntax-check; XAML/C++/WinRT reviewed for Windows build.

## Stage 3 — ClientApp (WinUI3 + ClientEngine)
Goal: elevated agent: discover→connect→handle POWERSHELL/FILE_PATH/INSTALL/FIX/SET_DNS/TOAST/CLOSE.
Validation: command-dispatch table review + input-validation audit.

## Stage 4 — Solution + Installer + docs
Goal: OSFM-Net.sln, .vcxproj, MSIX manifests, Installer/*.ps1, docs/PROTOCOL.md + SECURITY.md.
Validation: XML well-formed (xmllint), docs cross-check vs security_checklist.md.

## Stage 5 — Verification & Handoff
Goal: full syntax pass, secret scan (grep), final README.
Validation: g++ clean, no secrets in diff, no TODOs without issues.

Security notes (security_checklist + data_handling): passwords never logged (redacted),
all TCP input validated at boundary (prefix allow-list, size caps, hostname/pkgId sanitized),
DNS/user inputs validated, least-privilege (server highestAvailable / client requireAdmin),
no PII in logs beyond hostname (Internal), generic client-facing errors.

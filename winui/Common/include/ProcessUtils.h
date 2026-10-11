#pragma once
// Process launching: hidden capture, elevated relaunch, mstsc RDP, SMB-safe installer walk.

#include <string>

namespace osfm::proc {

struct Result {
    unsigned long exitCode = 0;
    std::string out;
    std::string err;
    bool launched = false;
};

// Run `commandLine` hidden, capture stdout/stderr, wait up to timeoutMs (INFINITE default).
Result RunCapture(const std::wstring& commandLine, unsigned long timeoutMs = 0xFFFFFFFF);

// Fire-and-forget (used for mstsc, installers that need a visible window).
bool StartDetached(const std::wstring& commandLine);

// Relaunch `exe args` elevated ("runas" verb).
bool RunElevated(const std::wstring& exe, const std::wstring& args);

// Double-click client -> Remote Desktop.
bool OpenRdp(const std::wstring& host);

// PowerShell -NoProfile -ExecutionPolicy Bypass -Command <ps>
Result RunPowerShell(const std::wstring& ps, unsigned long timeoutMs = 0xFFFFFFFF);

// Walk \\HOST\osfm-temp\<pkg> for .exe/.msi and run each /quiet (or /qn for msi).
bool InstallFromShareDir(const std::wstring& dir, std::string* log = nullptr);

} // namespace osfm::proc

#pragma once
// Elevation, SMB share, firewall, RDP, DNS, users, repair — all privileged ops.
// Every function assumes it may be called unelevated; those that need admin
// return false with GetLastError() set, and callers use EnsureElevated().

#include <string>

namespace osfm::priv {

bool IsElevated();
// Relaunches current exe with `args` via ShellExecuteEx("runas"). Does not wait.
// Returns true if the elevate prompt was launched.
bool EnsureElevated(const wchar_t* args = nullptr);

// Creates/keeps SMB share `shareName -> path` with Everyone:FULL (NetShareAdd,
// fallback to New-SmbShare). Requires admin.
bool EnsureSmbShare(const std::wstring& shareName, const std::wstring& path);

// Opens TCP+UDP `port` in Windows Firewall (netsh advfirewall). Requires admin.
bool EnsureFirewallRule(unsigned short port);

// RDP enable: Private profile + fDenyTSConnections=0 + firewall group + TermService restart.
bool EnableRdp(std::wstring* log = nullptr);

// DNS helpers executed on the CLIENT via POWERSHELL transport (kept here for reuse/tests).
std::string DnsResetCommand();              // ResetServerAddresses
std::string DnsDisableCommand();            // 0.0.0.0
std::string DnsSetCommand(const std::string& dnsIp);

// Local user management command builders (server sends these as POWERSHELL).
std::string CreateUserCommand(const std::string& user, const std::string& pass);
std::string DeleteUserCommand(const std::string& user);

std::wstring DefaultTempDir();   // %ProgramData%\OSFM\osfm-temp
std::wstring UncTempPath(const std::wstring& host, const std::wstring& pkgId);

} // namespace osfm::priv

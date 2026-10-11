// Privilege.cpp — elevation, SMB share, firewall, RDP (all Windows-only).

#include "Privilege.h"
#include "NetUtils.h"
#include "ProcessUtils.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>
#include <lm.h>
#pragma comment(lib, "Netapi32.lib")
#pragma comment(lib, "Shell32.lib")

#include <cstdlib> // free (_wdupenv_s)
#include <string>

namespace osfm::priv {

bool IsElevated() {
    HANDLE tok = nullptr;
    if (!::OpenProcessToken(::GetCurrentProcess(), TOKEN_QUERY, &tok)) return false;
    TOKEN_ELEVATION e{};
    DWORD n = 0;
    bool ok = !!::GetTokenInformation(tok, TokenElevation, &e, sizeof(e), &n) && e.TokenIsElevated;
    ::CloseHandle(tok);
    return ok;
}

bool EnsureElevated(const wchar_t* args) {
    wchar_t exe[MAX_PATH]{};
    ::GetModuleFileNameW(nullptr, exe, MAX_PATH);
    return proc::RunElevated(exe, args ? args : L"");
}

bool EnsureSmbShare(const std::wstring& shareName, const std::wstring& path) {
    ::CreateDirectoryW(path.c_str(), nullptr);
    SHARE_INFO_502 si{};
    si.shi502_netname = const_cast<LPWSTR>(shareName.c_str());
    si.shi502_type = STYPE_DISKTREE;
    si.shi502_remark = L"OSFM software staging";
    si.shi502_permissions = ACCESS_ALL;
    si.shi502_max_uses = static_cast<DWORD>(-1);
    si.shi502_path = const_cast<LPWSTR>(path.c_str());
    si.shi502_passwd = nullptr;
    DWORD err = 0;
    NET_API_STATUS st = ::NetShareAdd(nullptr, 502,
        reinterpret_cast<LPBYTE>(&si), &err);
    if (st == NERR_Success || st == NERR_DuplicateShare) return true;
    // Fallback mirrors ensure_temp_folder_shared(): New-SmbShare ... -FullAccess Everyone
    std::wstring ps = L"New-SmbShare -Name '" + shareName + L"' -Path '" + path +
                      L"' -FullAccess Everyone -ErrorAction Stop";
    return proc::RunPowerShell(ps).exitCode == 0;
}

bool EnsureFirewallRule(unsigned short port) {
    std::wstring p = std::to_wstring(port);
    std::wstring tcp = L"netsh advfirewall firewall add rule name=\"OSFM-Net TCP " +
        p + L"\" dir=in action=allow protocol=TCP localport=" + p;
    std::wstring udp = L"netsh advfirewall firewall add rule name=\"OSFM-Net UDP " +
        p + L"\" dir=in action=allow protocol=UDP localport=" + p;
    return proc::RunCapture(tcp).exitCode == 0 &&
           proc::RunCapture(udp).exitCode == 0;
}

bool EnableRdp(std::wstring* log) {
    // Parity with enable_rdp(): Private profile -> fDenyTSConnections=0 ->
    // firewall group -> restart TermService.
    std::wstring ps =
        L"Get-NetConnectionProfile | Where-Object {$_.NetworkCategory -eq 'Public'} | "
        L"Set-NetConnectionProfile -NetworkCategory Private; "
        L"Set-ItemProperty -Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Control\\Terminal Server' "
        L"-Name 'fDenyTSConnections' -Value 0; "
        L"Enable-NetFirewallRule -DisplayGroup 'Remote Desktop'; "
        L"Restart-Service -Name 'TermService' -Force";
    auto r = proc::RunPowerShell(ps, 120000);
    if (log) *log = r.out + r.err; // narrow output: log directly, no ToNarrow
    return r.exitCode == 0;
}

std::string DnsResetCommand() {
    return "Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ResetServerAddresses";
}
std::string DnsDisableCommand() {
    return "Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ServerAddresses '0.0.0.0'";
}
std::string DnsSetCommand(const std::string& dnsIp) {
    return "Set-DnsClientServerAddress -InterfaceAlias 'Ethernet' -ServerAddresses " + dnsIp;
}
std::string CreateUserCommand(const std::string& user, const std::string& pass) {
    return "net user " + user + " " + pass + " /add ; net localgroup Administrators " + user + " /add";
}
std::string DeleteUserCommand(const std::string& user) {
    return "net user " + user + " /delete";
}

std::wstring DefaultTempDir() {
    wchar_t* buf = nullptr;
    size_t n = 0;
    if (_wdupenv_s(&buf, &n, L"ProgramData") == 0 && buf) {
        std::wstring d = std::wstring(buf) + L"\\OSFM\\osfm-temp";
        free(buf);
        return d;
    }
    return L"C:\\ProgramData\\OSFM\\osfm-temp";
}

std::wstring UncTempPath(const std::wstring& host, const std::wstring& pkgId) {
    return L"\\\\" + host + L"\\osfm-temp\\" + pkgId;
}

} // namespace osfm::priv
#else
namespace osfm::priv {
bool IsElevated() { return false; }
bool EnsureElevated(const wchar_t*) { return false; }
bool EnsureSmbShare(const std::wstring&, const std::wstring&) { return false; }
bool EnsureFirewallRule(unsigned short) { return false; }
bool EnableRdp(std::wstring*) { return false; }
std::string DnsResetCommand() { return {}; }
std::string DnsDisableCommand() { return {}; }
std::string DnsSetCommand(const std::string&) { return {}; }
std::string CreateUserCommand(const std::string&, const std::string&) { return {}; }
std::string DeleteUserCommand(const std::string&) { return {}; }
std::wstring DefaultTempDir() { return L"/tmp/osfm-temp"; }
std::wstring UncTempPath(const std::wstring& h, const std::wstring& p) { return L"\\\\" + h + L"\\osfm-temp\\" + p; }
} // namespace osfm::priv
#endif

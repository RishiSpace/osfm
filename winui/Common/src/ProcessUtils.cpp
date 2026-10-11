// ProcessUtils.cpp — hidden capture, elevated launch, RDP, share-dir install.

#include "ProcessUtils.h"
#include "NetUtils.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <shellapi.h>

#include <cwctype>
#include <filesystem>
#include <vector>

namespace osfm::proc {

static std::string ReadPipe(HANDLE h) {
    std::string out;
    char buf[4096];
    DWORD n = 0;
    while (::ReadFile(h, buf, sizeof(buf), &n, nullptr) && n > 0)
        out.append(buf, n);
    return out;
}

Result RunCapture(const std::wstring& commandLine, unsigned long timeoutMs) {
    Result r;
    SECURITY_ATTRIBUTES sa{sizeof(sa), nullptr, TRUE};
    HANDLE ro = nullptr, wo = nullptr, re = nullptr, we = nullptr;
    if (!::CreatePipe(&ro, &wo, &sa, 0)) return r;
    if (!::CreatePipe(&re, &we, &sa, 0)) { ::CloseHandle(ro); ::CloseHandle(wo); return r; }
    ::SetHandleInformation(ro, HANDLE_FLAG_INHERIT, 0);
    ::SetHandleInformation(re, HANDLE_FLAG_INHERIT, 0);

    STARTUPW si{};
    si.cb = sizeof(si);
    si.dwFlags = STARTF_USESTDHANDLES | STARTF_USESHOWWINDOW;
    si.wShowWindow = SW_HIDE;
    si.hStdOutput = wo;
    si.hStdError = we;
    PROCESS_INFORMATION pi{};
    std::wstring cmd = commandLine; // CreateProcess may mutate
    if (!::CreateProcessW(nullptr, cmd.data(), nullptr, nullptr, TRUE,
                          CREATE_NO_WINDOW, nullptr, nullptr, &si, &pi)) {
        ::CloseHandle(ro); ::CloseHandle(wo);
        ::CloseHandle(re); ::CloseHandle(we);
        return r;
    }
    ::CloseHandle(wo); ::CloseHandle(we);
    r.launched = true;
    ::WaitForSingleObject(pi.hProcess, timeoutMs);
    r.out = ReadPipe(ro);
    r.err = ReadPipe(re);
    DWORD code = 0;
    ::GetExitCodeProcess(pi.hProcess, &code);
    r.exitCode = code;
    ::CloseHandle(ro); ::CloseHandle(re);
    ::CloseHandle(pi.hProcess); ::CloseHandle(pi.hThread);
    return r;
}

bool StartDetached(const std::wstring& commandLine) {
    STARTUPW si{};
    si.cb = sizeof(si);
    PROCESS_INFORMATION pi{};
    std::wstring cmd = commandLine;
    bool ok = !!::CreateProcessW(nullptr, cmd.data(), nullptr, nullptr, FALSE,
                                 DETACHED_PROCESS, nullptr, nullptr, &si, &pi);
    if (ok) { ::CloseHandle(pi.hProcess); ::CloseHandle(pi.hThread); }
    return ok;
}

bool RunElevated(const std::wstring& exe, const std::wstring& args) {
    SHELLEXECUTEINFOW sei{};
    sei.cbSize = sizeof(sei);
    sei.fMask = SEE_MASK_NOCLOSEPROCESS;
    sei.lpVerb = L"runas";
    sei.lpFile = exe.c_str();
    sei.lpParameters = args.empty() ? nullptr : args.c_str();
    sei.nShow = SW_NORMAL;
    if (!::ShellExecuteExW(&sei)) return false;
    if (sei.hProcess) ::CloseHandle(sei.hProcess);
    return true;
}

bool OpenRdp(const std::wstring& host) {
    return StartDetached(L"mstsc /v:" + host); // parity with rdp_to_client()
}

Result RunPowerShell(const std::wstring& ps, unsigned long timeoutMs) {
    // Escape embedded quotes for -Command "..."
    std::wstring esc;
    esc.reserve(ps.size());
    for (wchar_t c : ps) esc += (c == L'"' ? L"\"\"" : std::wstring(1, c));
    return RunCapture(L"powershell.exe -NoProfile -ExecutionPolicy Bypass -Command \"" +
                      esc + L"\"", timeoutMs);
}

bool InstallFromShareDir(const std::wstring& dir, std::string* log) {
    namespace fs = std::filesystem;
    std::error_code ec;
    if (!fs::is_directory(dir, ec)) {
        if (log) *log = "not a directory: " + net::ToNarrow(dir);
        return false;
    }
    bool any = false;
    for (auto& e : fs::recursive_directory_iterator(dir, ec)) {
        if (ec) break;
        if (!e.is_regular_file()) continue;
        auto ext = e.path().extension().wstring();
        for (auto& c : ext) c = towlower(c);
        if (ext != L".exe" && ext != L".msi") continue;
        any = true;
        std::wstring args = (ext == L".msi")
            ? L"msiexec /i \"" + e.path().wstring() + L"\" /qn /norestart"
            : L"\"" + e.path().wstring() + L"\" /quiet";
        Result r = RunCapture(L"cmd.exe /c " + args, 20 * 60 * 1000);
        if (log) *log += net::ToNarrow(e.path().wstring()) +
                         " exit=" + std::to_string(r.exitCode) + "\n";
    }
    if (!any && log) *log = "no .exe/.msi under " + net::ToNarrow(dir);
    return any;
}

} // namespace osfm::proc
#else
namespace osfm::proc {
Result RunCapture(const std::wstring&, unsigned long) { return {}; }
bool StartDetached(const std::wstring&) { return false; }
bool RunElevated(const std::wstring&, const std::wstring&) { return false; }
bool OpenRdp(const std::wstring&) { return false; }
Result RunPowerShell(const std::wstring&, unsigned long) { return {}; }
bool InstallFromShareDir(const std::wstring&, std::string*) { return false; }
} // namespace osfm::proc
#endif

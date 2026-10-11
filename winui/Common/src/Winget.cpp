// Winget.cpp — server-side winget search/download (Windows-only execution).

#include "Winget.h"
#include "NetUtils.h"
#include "ProcessUtils.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

#include <cctype>
#include <cwctype>
#include <filesystem>
#include <string>
#include <vector>

namespace osfm::winget {

std::map<std::string, std::string> ParseSearchTable(const std::string& output) {
    // Port of parse_winget_output(): header-driven column slices.
    std::map<std::string, std::string> out;
    std::vector<std::string> lines;
    size_t pos = 0;
    while (pos < output.size()) {
        size_t e = output.find('\n', pos);
        std::string ln = output.substr(pos, e == std::string::npos ? e : e - pos);
        if (!ln.empty() && ln.back() == '\r') ln.pop_back();
        lines.push_back(ln);
        if (e == std::string::npos) break;
        pos = e + 1;
    }
    size_t hi = std::string::npos;
    for (size_t i = 0; i < lines.size(); ++i)
        if (lines[i].find("Name") != std::string::npos &&
            lines[i].find("Id") != std::string::npos) { hi = i; break; }
    if (hi == std::string::npos) return out;
    const std::string& h = lines[hi];
    size_t nameP = h.find("Name"), idP = h.find("Id"), verP = h.find("Version");
    if (nameP == std::string::npos || idP == std::string::npos ||
        verP == std::string::npos || !(nameP < idP && idP < verP))
        return out;
    for (size_t i = hi + 2; i < lines.size(); ++i) {
        const std::string& ln = lines[i];
        if (ln.size() < verP || ln.find_first_not_of(" -") == std::string::npos) continue;
        auto cell = [&](size_t a, size_t b) {
            std::string c = ln.substr(a, (b > ln.size() ? ln.size() : b) - a);
            size_t s = c.find_first_not_of(" \t"), e = c.find_last_not_of(" \t");
            return s == std::string::npos ? std::string{} : c.substr(s, e - s + 1);
        };
        std::string name = cell(nameP, idP), id = cell(idP, verP);
        if (!name.empty() && !id.empty()) out[name] = id;
    }
    return out;
}

#ifdef _WIN32
std::vector<Package> Search(const std::string& term, std::string* err) {
    std::vector<Package> pkgs;
    if (term.empty()) return pkgs;
    auto r = proc::RunCapture(
        net::ToWide("winget search " + term + " --source winget"), 60000);
    if (r.exitCode != 0) {
        if (err) *err = r.err.empty() ? r.out : r.err;
        return pkgs;
    }
    for (auto& [name, id] : ParseSearchTable(r.out))
        pkgs.push_back({name, id, {}});
    return pkgs;
}

bool Download(const std::string& id, const std::wstring& dir, std::string* log) {
    ::CreateDirectoryW(dir.c_str(), nullptr);
    auto r = proc::RunCapture(
        L"winget download --id " + net::ToWide(id) + L" -d \"" + dir + L"\"",
        30 * 60 * 1000);
    if (log) *log = r.out + r.err;
    return r.exitCode == 0;
}

std::wstring FindInstaller(const std::wstring& dir) {
    namespace fs = std::filesystem;
    std::error_code ec;
    for (auto& e : fs::recursive_directory_iterator(dir, ec)) {
        if (ec) break;
        if (!e.is_regular_file()) continue;
        auto ext = e.path().extension().wstring();
        for (auto& c : ext) c = towlower(c);
        if (ext == L".exe" || ext == L".msi") return e.path().wstring();
    }
    return {};
}
#else
std::vector<Package> Search(const std::string&, std::string*) { return {}; }
bool Download(const std::string&, const std::wstring&, std::string*) { return false; }
std::wstring FindInstaller(const std::wstring&) { return {}; }
#endif

} // namespace osfm::winget

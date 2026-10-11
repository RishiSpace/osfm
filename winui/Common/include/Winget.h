#pragma once
// winget wrappers on the SERVER: search (parsed to name->id), download, uninstall cmd builder.
// Mirrors parse_winget_output() from server.py.

#include <map>
#include <string>
#include <vector>

namespace osfm::winget {

struct Package {
    std::string name;
    std::string id;
    std::string version;
};

// Runs `winget search <term> --source winget` and parses the table output.
std::vector<Package> Search(const std::string& term, std::string* err = nullptr);

// Column-position parser (header-driven: Name/Id/Version[/Match][/Source]).
std::map<std::string, std::string> ParseSearchTable(const std::string& output);

// `winget download --id <id> -d <dir>`; returns true on exit 0.
bool Download(const std::string& id, const std::wstring& dir, std::string* log = nullptr);

// Command the server broadcasts for uninstall (client runs via POWERSHELL).
inline std::string UninstallCommand(const std::string& id) {
    return "winget uninstall --id \"" + id + "\"";
}

// First .exe/.msi found recursively under dir, "" if none.
std::wstring FindInstaller(const std::wstring& dir);

} // namespace osfm::winget

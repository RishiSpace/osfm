#pragma once
// OSFM wire protocol — MUST stay compatible with the Python implementation.
// Port 12345, plain UTF-8 text commands (single recv framing, as legacy).

#include <string>

namespace osfm {

inline constexpr unsigned short kPort = 12345;
inline constexpr const char* kDiscoverRequest  = "DISCOVER_SERVER";
inline constexpr const char* kDiscoverResponse = "SERVER_HERE";
inline constexpr const char* kOk    = "200 OK";
inline constexpr const char* kError = "500 ERROR";

// Server -> client prefixes
inline constexpr const char* kPsPrefix       = "POWERSHELL "; // + powershell body
inline constexpr const char* kFilePathPrefix = "FILE_PATH ";  // + \\HOST\osfm-temp\<pkg>
inline constexpr const char* kInstall        = "INSTALL";
inline constexpr const char* kFix            = "FIX";
inline constexpr const char* kSetDnsPrefix   = "SET_DNS ";    // + dns ip
inline constexpr const char* kToastCPrefix   = "TOASTC ";     // + user created
inline constexpr const char* kToastDPrefix   = "TOASTD ";     // + user deleted
inline constexpr const char* kClose          = "CLOSE";
inline constexpr const char* kHostPrefix     = "HOSTNAME ";   // client hello

inline bool StartsWith(const std::string& s, const char* prefix) {
    const std::string p(prefix);
    return s.size() >= p.size() && s.compare(0, p.size(), p) == 0;
}

inline std::string AfterPrefix(const std::string& s, const char* prefix) {
    const std::string p(prefix);
    return s.size() > p.size() ? s.substr(p.size()) : std::string{};
}

} // namespace osfm

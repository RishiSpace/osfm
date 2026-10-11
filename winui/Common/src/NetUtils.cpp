// NetUtils.cpp — Winsock helpers for OSFM-Net (WinUI 3 overhaul).
// NOTE: Builds on Windows only (winsock2). Kept Win32-free in the header.

#include "NetUtils.h"
#include "OsfmProtocol.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")

#include <cstring> // strlen
#include <string>
#include <vector>

namespace osfm::net {

bool Startup() {
    WSADATA wsa{};
    return ::WSAStartup(MAKEWORD(2, 2), &wsa) == 0;
}

void Cleanup() { ::WSACleanup(); }

bool IsPortInUse(unsigned short port) {
    SOCKET s = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) return false;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);
    int rc = ::bind(s, reinterpret_cast<sockaddr*>(&addr), sizeof(addr));
    ::closesocket(s);
    return rc == SOCKET_ERROR; // in use (or no permission) -> treat as running
}

std::string GetHostname() {
    char buf[256]{};
    if (::gethostname(buf, sizeof(buf)) == 0) return std::string(buf);
    return "unknown-pc";
}

std::wstring ToWide(const std::string& s) {
    if (s.empty()) return {};
    int n = ::MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, nullptr, 0);
    if (n <= 0) return {};
    std::wstring w(static_cast<size_t>(n - 1), L'\0');
    ::MultiByteToWideChar(CP_UTF8, 0, s.c_str(), -1, &w[0], n);
    return w;
}

std::string ToNarrow(const std::wstring& ws) {
    if (ws.empty()) return {};
    int n = ::WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), -1, nullptr, 0, nullptr, nullptr);
    if (n <= 0) return {};
    std::string s(static_cast<size_t>(n - 1), '\0');
    ::WideCharToMultiByte(CP_UTF8, 0, ws.c_str(), -1, &s[0], n, nullptr, nullptr);
    return s;
}

bool SendAll(unsigned long long sock, const std::string& data) {
    SOCKET s = static_cast<SOCKET>(sock);
    const char* p = data.data();
    int left = static_cast<int>(data.size());
    while (left > 0) {
        int sent = ::send(s, p, left, 0);
        if (sent == SOCKET_ERROR) return false;
        p += sent;
        left -= sent;
    }
    return true;
}

bool RecvOnce(unsigned long long sock, std::string& out, int timeoutMs) {
    SOCKET s = static_cast<SOCKET>(sock);
    if (timeoutMs > 0) {
        DWORD tv = static_cast<DWORD>(timeoutMs);
        ::setsockopt(s, SOL_SOCKET, SO_RCVTIMEO,
                     reinterpret_cast<const char*>(&tv), sizeof(tv));
    }
    char buf[4096]{};
    int n = ::recv(s, buf, sizeof(buf) - 1, 0);
    if (n <= 0) return false;
    out.assign(buf, static_cast<size_t>(n));
    return true;
}

std::string DiscoverServer(unsigned short port, int timeoutMs) {
    SOCKET s = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s == INVALID_SOCKET) return {};
    BOOL b = TRUE;
    ::setsockopt(s, SOL_SOCKET, SO_BROADCAST, reinterpret_cast<const char*>(&b), sizeof(b));
    DWORD tv = static_cast<DWORD>(timeoutMs);
    ::setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, reinterpret_cast<const char*>(&tv), sizeof(tv));

    sockaddr_in dest{};
    dest.sin_family = AF_INET;
    dest.sin_port = htons(port);
    dest.sin_addr.s_addr = INADDR_BROADCAST;
    ::sendto(s, kDiscoverRequest, static_cast<int>(strlen(kDiscoverRequest)), 0,
             reinterpret_cast<sockaddr*>(&dest), sizeof(dest));

    char buf[64]{};
    sockaddr_in from{};
    int fromLen = sizeof(from);
    int n = ::recvfrom(s, buf, sizeof(buf) - 1, 0,
                       reinterpret_cast<sockaddr*>(&from), &fromLen);
    ::closesocket(s);
    if (n <= 0) return {};
    buf[n] = '\0';
    if (std::string(buf) != kDiscoverResponse) return {};
    char ip[INET_ADDRSTRLEN]{};
    ::inet_ntop(AF_INET, &from.sin_addr, ip, sizeof(ip));
    return std::string(ip);
}

} // namespace osfm::net
#else
// Non-Windows stubs so the tree can be inspected/parsed on Linux.
#include <cstring>
namespace osfm::net {
bool Startup() { return false; }
void Cleanup() {}
bool IsPortInUse(unsigned short) { return false; }
std::string GetHostname() { return "dev-linux"; }
std::wstring ToWide(const std::string& s) { return std::wstring(s.begin(), s.end()); }
std::string ToNarrow(const std::wstring& ws) { return std::string(ws.begin(), ws.end()); }
bool SendAll(unsigned long long, const std::string&) { return false; }
bool RecvOnce(unsigned long long, std::string&, int) { return false; }
std::string DiscoverServer(unsigned short, int) { return {}; }
} // namespace osfm::net
#endif

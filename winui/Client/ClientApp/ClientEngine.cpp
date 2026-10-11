// ClientEngine.cpp — discovery/connect/dispatch (Windows Winsock).

#include "ClientEngine.h"
#include "Logger.h"
#include "NetUtils.h"
#include "OsfmProtocol.h"
#include "Privilege.h"
#include "ProcessUtils.h"
#include "Toast.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")

#include <cctype>
#include <chrono>
#include <thread>

namespace osfm::client {

// --- LLMG security: allow-list + caps at the trust boundary ---
static bool SafeToken(const std::string& s) {
    if (s.empty() || s.size() > 64) return false;
    for (char c : s)
        if (!isalnum((unsigned char)c) && c != '-' && c != '_' && c != '.' &&
            c != '$')
            return false;
    return true;
}
static bool SafeDnsIp(const std::string& s) {
    if (s.empty() || s.size() > 64) return false;
    for (char c : s)
        if (!isalnum((unsigned char)c) && c != '.' && c != ':') return false;
    return true;
}

ClientEngine::ClientEngine(unsigned short port, Callbacks cb)
    : port_(port), cb_(std::move(cb)) {}
ClientEngine::~ClientEngine() { Stop(); }

void ClientEngine::Start() {
    net::Startup();
    std::string rdpLog;
    priv::EnableRdp(&rdpLog); // parity: client enables RDP on boot (elevated)
    stop_ = false;
    worker_ = std::thread(&ClientEngine::Worker, this);
}
void ClientEngine::Stop() {
    stop_ = true;
    if (worker_.joinable()) worker_.detach();
}

void ClientEngine::Ack(unsigned long long sock, bool ok) {
    net::SendAll(sock, ok ? kOk : kError);
}

bool ClientEngine::ConnectOnce(std::string& serverIp,
                               unsigned long long& sock) {
    serverIp = net::DiscoverServer(port_);
    if (serverIp.empty()) return false;
    SOCKET s = ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) return false;
    sockaddr_in a{};
    a.sin_family = AF_INET;
    a.sin_port = htons(port_);
    ::inet_pton(AF_INET, serverIp.c_str(), &a.sin_addr);
    if (::connect(s, reinterpret_cast<sockaddr*>(&a), sizeof(a)) != 0) {
        ::closesocket(s);
        return false;
    }
    std::string hello = std::string(kHostPrefix) + net::GetHostname();
    if (!net::SendAll(static_cast<unsigned long long>(s), hello)) {
        ::closesocket(s);
        return false;
    }
    // First frame is the server hostname; skip self-connect (parity).
    std::string banner;
    net::RecvOnce(static_cast<unsigned long long>(s), banner, 3000);
    if (banner == net::GetHostname()) {
        ::closesocket(s);
        return false;
    }
    sock = static_cast<unsigned long long>(s);
    return true;
}

void ClientEngine::RunFix(unsigned long long sock) {
    // Parity with fix_windows(): sfc /scannow + DISM Check/Scan/RestoreHealth.
    auto sfc = proc::RunCapture(L"sfc /scannow", 30 * 60 * 1000);
    auto dh = proc::RunCapture(L"DISM /Online /Cleanup-Image /CheckHealth",
                               30 * 60 * 1000);
    auto ds = proc::RunCapture(L"DISM /Online /Cleanup-Image /ScanHealth",
                               60 * 60 * 1000);
    auto dr = proc::RunCapture(L"DISM /Online /Cleanup-Image /RestoreHealth",
                               60 * 60 * 1000);
    Ack(sock, sfc.exitCode == 0 && dr.exitCode == 0);
    (void)dh;
    (void)ds;
}

void ClientEngine::Serve(unsigned long long sock) {
    SOCKET s = static_cast<SOCKET>(sock);
    toast::Show(L"OSFM-Control",
                L"This system is currently being controlled by an Administrator");
    while (!stop_) {
        char buf[1024]{};
        int n = ::recv(s, buf, sizeof(buf) - 1, 0);
        if (n <= 0) break;
        std::string cmd(buf, static_cast<size_t>(n));

        if (StartsWith(cmd, kPsPrefix)) {
            auto ps = net::ToWide(AfterPrefix(cmd, kPsPrefix));
            auto r = proc::RunPowerShell(ps, 10 * 60 * 1000);
            Ack(sock, r.exitCode == 0);
        } else if (StartsWith(cmd, kFilePathPrefix)) {
            lastShareDir_ = AfterPrefix(cmd, kFilePathPrefix);
            if (cb_.onLog) cb_.onLog("FILE_PATH " + lastShareDir_);
            Ack(sock, !lastShareDir_.empty()); // install happens on INSTALL
        } else if (cmd == kInstall || cmd.rfind(kInstall, 0) == 0) {
            std::string lg;
            bool ok = !lastShareDir_.empty() &&
                      proc::InstallFromShareDir(net::ToWide(lastShareDir_), &lg);
            if (cb_.onLog) cb_.onLog(lg);
            Ack(sock, ok);
        } else if (cmd == kFix || cmd.rfind(kFix, 0) == 0) {
            RunFix(sock);
        } else if (StartsWith(cmd, kSetDnsPrefix)) {
            auto ip = AfterPrefix(cmd, kSetDnsPrefix);
            if (!SafeDnsIp(ip)) {
                Ack(sock, false);
                continue;
            }
            auto r = proc::RunPowerShell(net::ToWide(priv::DnsSetCommand(ip)));
            Ack(sock, r.exitCode == 0);
        } else if (StartsWith(cmd, kToastCPrefix)) {
            auto u = AfterPrefix(cmd, kToastCPrefix);
            if (SafeToken(u))
                toast::Show(L"User Management", net::ToWide("User " + u + " created"));
            Ack(sock, SafeToken(u));
        } else if (StartsWith(cmd, kToastDPrefix)) {
            auto u = AfterPrefix(cmd, kToastDPrefix);
            if (SafeToken(u))
                toast::Show(L"User Management", net::ToWide("User " + u + " deleted"));
            Ack(sock, SafeToken(u));
        } else if (cmd == kClose || cmd.rfind(kClose, 0) == 0) {
            break;
        } else if (cb_.onLog) {
            cb_.onLog("unexpected: " + cmd);
        }
    }
    ::closesocket(s);
}

void ClientEngine::Worker() {
    while (!stop_) {
        std::string ip;
        unsigned long long sock = 0;
        if (!ConnectOnce(ip, sock)) {
            if (cb_.onState) cb_.onState("", false);
            std::this_thread::sleep_for(std::chrono::seconds(5)); // parity retry
            continue;
        }
        connected_ = true;
        if (cb_.onState) cb_.onState(ip, true);
        if (cb_.onLog) cb_.onLog("connected to " + ip);
        Serve(sock);
        connected_ = false;
        if (cb_.onState) cb_.onState(ip, false);
    }
}

} // namespace osfm::client
#else
namespace osfm::client {
ClientEngine::ClientEngine(unsigned short, Callbacks) {}
ClientEngine::~ClientEngine() {}
void ClientEngine::Start() {}
void ClientEngine::Stop() {}
} // namespace osfm::client
#endif

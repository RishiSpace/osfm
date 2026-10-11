// TcpServer.cpp — discovery responder + accept/handle loops (Windows Winsock).

#include "TcpServer.h"
#include "Logger.h"
#include "NetUtils.h"
#include "OsfmProtocol.h"

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib, "Ws2_32.lib")

namespace osfm::server {

TcpServer::TcpServer(unsigned short port, std::string serverHostname, Callbacks cb)
    : port_(port), hostname_(std::move(serverHostname)), cb_(std::move(cb)) {}

TcpServer::~TcpServer() { Stop(); }

bool TcpServer::Start() {
    net::Startup();
    listenSock_ = static_cast<unsigned long long>(
        ::socket(AF_INET, SOCK_STREAM, IPPROTO_TCP));
    if (static_cast<SOCKET>(listenSock_) == INVALID_SOCKET) return false;
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port_);
    if (::bind(static_cast<SOCKET>(listenSock_),
               reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0 ||
        ::listen(static_cast<SOCKET>(listenSock_), 5) != 0) {
        ::closesocket(static_cast<SOCKET>(listenSock_));
        listenSock_ = 0;
        return false;
    }
    running_ = true;
    udpThread_ = std::thread(&TcpServer::UdpLoop, this);
    acceptThread_ = std::thread(&TcpServer::AcceptLoop, this);
    return true;
}

void TcpServer::Stop() {
    running_ = false;
    if (listenSock_) {
        ::closesocket(static_cast<SOCKET>(listenSock_));
        listenSock_ = 0;
    }
    if (udpThread_.joinable()) udpThread_.detach();
    if (acceptThread_.joinable()) acceptThread_.detach();
}

void TcpServer::UdpLoop() {
    SOCKET s = ::socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
    if (s == INVALID_SOCKET) return;
    BOOL re = TRUE;
    ::setsockopt(s, SOL_SOCKET, SO_REUSEADDR,
                 reinterpret_cast<const char*>(&re), sizeof(re));
    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port_);
    if (::bind(s, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        ::closesocket(s);
        return;
    }
    char buf[64]{};
    while (running_) {
        sockaddr_in from{};
        int len = sizeof(from);
        int n = ::recvfrom(s, buf, sizeof(buf) - 1, 0,
                           reinterpret_cast<sockaddr*>(&from), &len);
        if (n > 0 && std::string(buf, static_cast<size_t>(n)) == kDiscoverRequest)
            ::sendto(s, kDiscoverResponse,
                     static_cast<int>(strlen(kDiscoverResponse)), 0,
                     reinterpret_cast<sockaddr*>(&from), len);
    }
    ::closesocket(s);
}

void TcpServer::AcceptLoop() {
    while (running_) {
        SOCKET c = ::accept(static_cast<SOCKET>(listenSock_), nullptr, nullptr);
        if (c == INVALID_SOCKET) {
            if (running_) ::Sleep(100);
            continue;
        }
        std::string hello;
        if (!net::RecvOnce(static_cast<unsigned long long>(c), hello)) {
            ::closesocket(c);
            continue;
        }
        char ip[INET_ADDRSTRLEN]{};
        sockaddr_in peer{};
        int plen = sizeof(peer);
        ::getpeername(c, reinterpret_cast<sockaddr*>(&peer), &plen);
        ::inet_ntop(AF_INET, &peer.sin_addr, ip, sizeof(ip));

        ClientInfo ci;
        ci.key = hello;
        ci.display = StartsWith(hello, kHostPrefix) ? AfterPrefix(hello, kHostPrefix) : hello;
        ci.address = ip;
        ci.sock = static_cast<unsigned long long>(c);
        {
            std::lock_guard<std::mutex> lk(mutex_);
            clients_[hello] = ci;
        }
        // Parity: server immediately sends its own hostname on connect.
        net::SendAll(ci.sock, hostname_);
        if (cb_.onConnect) cb_.onConnect(ci);
        std::thread(&TcpServer::ClientLoop, this, ci.sock, hello).detach();
    }
}

void TcpServer::ClientLoop(unsigned long long sock, std::string key) {
    SOCKET s = static_cast<SOCKET>(sock);
    while (running_) {
        char buf[1024]{};
        int n = ::recv(s, buf, sizeof(buf) - 1, 0);
        if (n <= 0) break;
        std::string msg(buf, static_cast<size_t>(n));
        if (msg == kOk || msg.rfind(kOk, 0) == 0) {
            std::lock_guard<std::mutex> lk(mutex_);
            auto it = clients_.find(key);
            if (it != clients_.end()) it->second.status = "OK";
            if (cb_.onAck) cb_.onAck(key, true);
        } else if (msg == kError || msg.rfind(kError, 0) == 0) {
            std::lock_guard<std::mutex> lk(mutex_);
            auto it = clients_.find(key);
            if (it != clients_.end()) it->second.status = "ERROR";
            if (cb_.onAck) cb_.onAck(key, false);
        } else if (cb_.onLog) {
            cb_.onLog("[" + key + "] " + msg);
        }
    }
    ::closesocket(s);
    {
        std::lock_guard<std::mutex> lk(mutex_);
        clients_.erase(key);
    }
    if (cb_.onDisconnect) cb_.onDisconnect(key);
}

void TcpServer::Broadcast(const std::string& command) {
    std::lock_guard<std::mutex> lk(mutex_);
    for (auto& [k, c] : clients_) {
        c.status = "PENDING";
        if (!net::SendAll(c.sock, command) && cb_.onLog)
            cb_.onLog("send failed -> " + k);
    }
}

bool TcpServer::SendTo(const std::string& key, const std::string& command) {
    std::lock_guard<std::mutex> lk(mutex_);
    auto it = clients_.find(key);
    if (it == clients_.end()) return false;
    return net::SendAll(it->second.sock, command);
}

std::vector<ClientInfo> TcpServer::Clients() const {
    std::lock_guard<std::mutex> lk(mutex_);
    std::vector<ClientInfo> v;
    for (auto& [k, c] : clients_) v.push_back(c);
    return v;
}

size_t TcpServer::Completed() const {
    std::lock_guard<std::mutex> lk(mutex_);
    size_t n = 0;
    for (auto& [k, c] : clients_)
        if (c.status == "OK" || c.status == "ERROR") ++n;
    return n;
}

} // namespace osfm::server
#else
// Linux inspection stubs.
#include <utility>
namespace osfm::server {
TcpServer::TcpServer(unsigned short, std::string, Callbacks) {}
TcpServer::~TcpServer() {}
bool TcpServer::Start() { return false; }
void TcpServer::Stop() {}
void TcpServer::Broadcast(const std::string&) {}
bool TcpServer::SendTo(const std::string&, const std::string&) { return false; }
std::vector<ClientInfo> TcpServer::Clients() const { return {}; }
size_t TcpServer::Completed() const { return 0; }
} // namespace osfm::server
#endif

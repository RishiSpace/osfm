#pragma once
// Server TCP+UDP engine: UDP discovery responder + per-client threads.
// Mirrors Server.tcp_server/udp_listener/handle_client from server.py.
// UI-agnostic: reports events through Callbacks so MainWindow stays thin.

#include <atomic>
#include <functional>
#include <map>
#include <mutex>
#include <string>
#include <thread>
#include <vector>

namespace osfm::server {

struct ClientInfo {
    std::string key;       // "HOSTNAME <pc>" as received (map key, like Python)
    std::string display;   // hostname with prefix stripped
    std::string address;
    unsigned long long sock = 0;
    std::string status = "PENDING"; // PENDING | OK | ERROR
};

struct Callbacks {
    std::function<void(const ClientInfo&)> onConnect;
    std::function<void(const std::string& key)> onDisconnect;
    std::function<void(const std::string& key, bool ok)> onAck; // 200 OK / 500 ERROR
    std::function<void(const std::string& line)> onLog;
};

class TcpServer {
public:
    TcpServer(unsigned short port, std::string serverHostname, Callbacks cb);
    ~TcpServer();

    bool Start();   // binds, spawns UDP responder + TCP accept loop
    void Stop();
    // Broadcast raw command to all clients, reset statuses to PENDING (parity).
    void Broadcast(const std::string& command);
    // Send FILE_PATH to one client.
    bool SendTo(const std::string& key, const std::string& command);
    std::vector<ClientInfo> Clients() const;
    size_t Completed() const; // OK + ERROR count (drives progress bar)

private:
    void UdpLoop();
    void AcceptLoop();
    void ClientLoop(unsigned long long sock, std::string key);

    unsigned short port_;
    std::string hostname_;
    Callbacks cb_;
    std::atomic<bool> running_{false};
    unsigned long long listenSock_ = 0;
    std::thread udpThread_, acceptThread_;
    mutable std::mutex mutex_;
    std::map<std::string, ClientInfo> clients_;
};

} // namespace osfm::server

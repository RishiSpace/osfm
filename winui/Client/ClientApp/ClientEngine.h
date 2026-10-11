#pragma once
// ClientEngine — elevated agent: discover -> TCP connect -> dispatch loop.
// Handles: FILE_PATH, POWERSHELL, FIX, SET_DNS, TOASTC/D, INSTALL, CLOSE.
// Replies "200 OK" / "500 ERROR" so the server progress bar tracks acks.

#include <atomic>
#include <functional>
#include <string>
#include <thread>

namespace osfm::client {

struct Callbacks {
    std::function<void(const std::string& line)> onLog;
    std::function<void(const std::string& serverIp, bool connected)> onState;
};

class ClientEngine {
public:
    ClientEngine(unsigned short port, Callbacks cb);
    ~ClientEngine();
    void Start();   // enables RDP, spawns worker thread
    void Stop();
    bool IsConnected() const { return connected_; }

private:
    void Worker();
    bool ConnectOnce(std::string& serverIp, unsigned long long& sock);
    void Serve(unsigned long long sock);
    void Ack(unsigned long long sock, bool ok);
    void RunFix(unsigned long long sock);

    unsigned short port_;
    Callbacks cb_;
    std::atomic<bool> stop_{false};
    std::atomic<bool> connected_{false};
    std::thread worker_;
    std::string lastShareDir_; // set by FILE_PATH, consumed by INSTALL
};

} // namespace osfm::client

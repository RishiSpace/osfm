#pragma once
// Winsock helpers: hostname, single-instance port probe, send/recv-all, UTF conversions.

#include <string>
#include <vector>

namespace osfm::net {

bool Startup();
void Cleanup();

// True if something already listens on 127.0.0.1:port (server single-instance guard).
bool IsPortInUse(unsigned short port);

std::string GetHostname();
std::wstring ToWide(const std::string& s);
std::string ToNarrow(const std::wstring& ws);

bool SendAll(unsigned long long sock, const std::string& data);
bool RecvOnce(unsigned long long sock, std::string& out, int timeoutMs = 0);

// UDP broadcast "DISCOVER_SERVER", returns responder IP or "" on timeout.
// Implemented on raw SOCKET stored as unsigned long long to keep header Win32-free.
std::string DiscoverServer(unsigned short port, int timeoutMs = 5000);

} // namespace osfm::net

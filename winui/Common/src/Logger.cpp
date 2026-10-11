// Logger.cpp — rolling file + debugger + UI sink log.

#include "Logger.h"
#include "NetUtils.h" // ToWide: log file is UTF-16, lines are UTF-8

#include <chrono>
#include <ctime>
#include <filesystem>
#include <fstream>
#include <mutex>
#include <string>

#ifdef _WIN32
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#endif

namespace osfm::log {
namespace {
std::mutex g_mutex;
std::wofstream g_file;
Sink g_ui;
} // namespace

static std::string Stamp() {
    std::time_t t = std::time(nullptr);
    char buf[32]{};
#ifdef _WIN32
    struct tm tmv{};
    localtime_s(&tmv, &t);
    strftime(buf, sizeof(buf), "%H:%M:%S", &tmv);
#else
    strftime(buf, sizeof(buf), "%H:%M:%S", std::localtime(&t));
#endif
    return std::string("[") + buf + "] ";
}

static void Emit(const char* lvl, const std::string& msg) {
    std::string line = Stamp() + lvl + msg;
    Sink ui;
    {
        std::lock_guard<std::mutex> lk(g_mutex);
        ui = g_ui;
        if (g_file.is_open()) {
            // wofstream has no operator<<(const char*): convert first.
            g_file << net::ToWide(line) << L'\n';
            g_file.flush();
        }
    }
#ifdef _WIN32
    OutputDebugStringA((line + "\n").c_str());
#endif
    if (ui) ui(line);
}

void Init(const std::wstring& filePath) {
    std::lock_guard<std::mutex> lk(g_mutex);
    if (g_file.is_open()) g_file.close();
    // MSVC's wofstream::open takes (const wchar_t*) — pass c_str() directly.
    g_file.open(filePath.c_str(), std::ios::app);
}

void SetUiSink(Sink sink) {
    std::lock_guard<std::mutex> lk(g_mutex);
    g_ui = std::move(sink);
}

void Info(const std::string& msg) { Emit("", msg); }
void Warn(const std::string& msg) { Emit("[warn] ", msg); }
void Error(const std::string& msg) { Emit("[error] ", msg); }

} // namespace osfm::log

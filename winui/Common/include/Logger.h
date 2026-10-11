#pragma once
// Thread-safe rolling log: sink to debugger, file, and UI callback.

#include <functional>
#include <string>

namespace osfm::log {

using Sink = std::function<void(const std::string& line)>;

void Init(const std::wstring& filePath);   // also echoes to OutputDebugString
void SetUiSink(Sink sink);                 // MainWindow log pane
void Info(const std::string& msg);
void Warn(const std::string& msg);
void Error(const std::string& msg);

} // namespace osfm::log

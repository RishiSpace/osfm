#pragma once
// Windows 11 toast notifications via WinRT ToastNotificationManager.
// Replaces win10toast / plyer usage in the Python build.

#include <string>
#include <vector>

namespace osfm::toast {

// Shows a simple text toast: <title>\n<message>. Returns true if dispatched.
bool Show(const std::wstring& title, const std::wstring& message);
bool ShowNarrow(const std::string& title, const std::string& message);

} // namespace osfm::toast

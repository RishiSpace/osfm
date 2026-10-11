// Toast.cpp — WinRT toast notifications (replaces win10toast/plyer).
// NOTE: OsfmCore has NO CppWinRT PackageReference of its own. This TU
// includes <winrt/...> projection headers resolved from the consuming app's
// restored packages, so it MUST see the same CppWinRT version as the apps
// (else LNK2038 C++/WinRT version mismatch at link). Keep the solution on a
// single CppWinRT version; bump ServerApp/ClientApp together.

#include "Toast.h"
#include "NetUtils.h"

#ifdef _WIN32
#include <winrt/Windows.Data.Xml.Dom.h>
#include <winrt/Windows.UI.Notifications.h>

namespace osfm::toast {

bool Show(const std::wstring& title, const std::wstring& message) {
    try {
        using namespace winrt::Windows::Data::Xml::Dom;
        using namespace winrt::Windows::UI::Notifications;
        XmlDocument doc;
        doc.LoadXml(L"<toast><visual><binding template='ToastGeneric'>"
                    L"<text></text><text></text>"
                    L"</binding></visual></toast>");
        auto texts = doc.GetElementsByTagName(L"text");
        texts.Item(0).AppendChild(doc.CreateTextNode(title));
        texts.Item(1).AppendChild(doc.CreateTextNode(message));
        ToastNotification toast(doc);
        // Classic-desktop fallback AUMID: PowerShell's, guaranteed present.
        ToastNotificationManager::CreateToastNotifier(
            L"{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}\\WindowsPowerShell\\v1.0\\powershell.exe")
            .Show(toast);
        return true;
    } catch (...) {
        return false;
    }
}

bool ShowNarrow(const std::string& title, const std::string& message) {
    return Show(net::ToWide(title), net::ToWide(message));
}

} // namespace osfm::toast
#else
namespace osfm::toast {
bool Show(const std::wstring&, const std::wstring&) { return false; }
bool ShowNarrow(const std::string&, const std::string&) { return false; }
} // namespace osfm::toast
#endif

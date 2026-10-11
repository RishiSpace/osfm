// MainWindow.xaml.cpp — minimal status UI over ClientEngine.

#include "pch.h"
#include "MainWindow.xaml.h"
// InitializeComponent + control accessors come from MainWindow.xaml codegen
// via MainWindow.xaml.h's MainWindow.g.h include (backed by MainWindow.idl).
// Do NOT include MainWindow.g.cpp (it only exists for IDL-less pages).

#include "ClientEngine.h"
#include "Logger.h"
#include "NetUtils.h"
#include "OsfmProtocol.h"
#include "Privilege.h"

using namespace winrt;
using namespace Microsoft::UI::Xaml;
using namespace Microsoft::UI::Xaml::Controls;

namespace winrt::OSFM::ClientApp::implementation {

static hstring W(const std::string& s) { return hstring(osfm::net::ToWide(s)); }

MainWindow::MainWindow() {
    InitializeComponent();
    osfm::log::Init(L"OSFM-Client.log");
    osfm::log::SetUiSink([this](const std::string& line) {
        DispatcherQueue().TryEnqueue([this, line] {
            LogBox().Text(LogBox().Text() + W(line + "\n"));
        });
    });
    // Client MUST run elevated (RDP, DNS, SFC/DISM, installs). Relaunch if not.
    if (!osfm::priv::IsElevated()) {
        StateBar().Title(hstring(L"Restarting elevated (admin required)…"));
        osfm::priv::EnsureElevated(nullptr);
        return;
    }
    osfm::client::Callbacks cb;
    auto dq = DispatcherQueue();
    cb.onLog = [](const std::string& l) { osfm::log::Info(l); };
    cb.onState = [this, dq](const std::string& ip, bool up) {
        dq.TryEnqueue([this, ip, up] {
            StateBar().Title(up ? W("Controlled by " + ip) : hstring(L"Searching for server…"));
            StateBar().Severity(up ? InfoBarSeverity::Success : InfoBarSeverity::Informational);
            DetailText().Text(up ? W("Connected to " + ip + " on port 12345.")
                                 : hstring(L"UDP discovery on port 12345…"));
        });
    };
    engine_ = std::make_unique<osfm::client::ClientEngine>(osfm::kPort, std::move(cb));
    engine_->Start();
}

} // namespace winrt::OSFM::ClientApp::implementation

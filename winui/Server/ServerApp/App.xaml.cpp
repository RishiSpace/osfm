// App.xaml.cpp — ServerApp entry: single-instance guard + main window.

#include "pch.h"
#include "App.xaml.h"
#if __has_include("App.g.cpp")
#include "App.g.cpp"
#endif
#include "MainWindow.xaml.h"
#include "NetUtils.h"
#include "OsfmProtocol.h"

using namespace winrt;
using namespace Microsoft::UI::Xaml;

namespace winrt::OSFM::ServerApp::implementation {

App::App() { InitializeComponent(); }

void App::OnLaunched(LaunchActivatedEventArgs const&) {
    osfm::net::Startup();
    if (osfm::net::IsPortInUse(osfm::kPort)) return; // existing server guard
    window_ = make<MainWindow>();
    window_.Activate();
}

} // namespace winrt::OSFM::ServerApp::implementation

// App.xaml.cpp — ServerApp entry: single-instance guard + main window.

#include "pch.h"
#include "App.xaml.h"
// App_base + XamlTypeInfo glue come from App.idl (cppwinrt) + App.xaml
// codegen; do NOT include App.g.cpp (it only exists for IDL-less pages).
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

// Unpackaged WinAppSDK entry point: Application::Start calls OnLaunched.
int __stdcall wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    winrt::init_apartment(winrt::apartment_type::single_threaded);
    ::winrt::Microsoft::UI::Xaml::Application::Start(
        [](auto&&) { ::winrt::make<::winrt::OSFM::ServerApp::implementation::App>(); });
    return 0;
}

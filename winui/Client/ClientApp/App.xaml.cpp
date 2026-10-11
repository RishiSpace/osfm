// App.xaml.cpp — ClientApp entry (no single-instance guard; many clients).

#include "pch.h"
#include "App.xaml.h"
// App_base + XamlTypeInfo glue come from App.idl (cppwinrt) + App.xaml
// codegen; do NOT include App.g.cpp (it only exists for IDL-less pages).
#include "MainWindow.xaml.h"

using namespace winrt;
using namespace Microsoft::UI::Xaml;

namespace winrt::OSFM::ClientApp::implementation {

App::App() { InitializeComponent(); }

void App::OnLaunched(LaunchActivatedEventArgs const&) {
    window_ = make<MainWindow>();
    window_.Activate();
}

} // namespace winrt::OSFM::ClientApp::implementation

// Unpackaged WinAppSDK entry point: Application::Start calls OnLaunched.
int __stdcall wWinMain(HINSTANCE, HINSTANCE, PWSTR, int) {
    winrt::init_apartment(winrt::apartment_type::single_threaded);
    ::winrt::Microsoft::UI::Xaml::Application::Start(
        [](auto&&) { ::winrt::make<::winrt::OSFM::ClientApp::implementation::App>(); });
    return 0;
}

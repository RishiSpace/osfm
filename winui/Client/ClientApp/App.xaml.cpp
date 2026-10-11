// App.xaml.cpp — ClientApp entry (no single-instance guard; many clients).

#include "pch.h"
#include "App.xaml.h"
#if __has_include("App.g.cpp")
#include "App.g.cpp"
#endif
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

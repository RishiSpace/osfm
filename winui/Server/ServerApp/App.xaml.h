#pragma once
// App.g.h (cppwinrt, from App.idl) declares implementation::App_base;
// App.xaml.g.h (XAML compiler) declares AppT deriving from it.
// The .g.h MUST come first (mirrors MainWindow.xaml.h including MainWindow.g.h).
#include "App.g.h"
#include "App.xaml.g.h"
#include <winrt/Microsoft.UI.Xaml.h>

namespace winrt::OSFM::ServerApp::implementation {
struct App : AppT<App> {
    App();
    void OnLaunched(winrt::Microsoft::UI::Xaml::LaunchActivatedEventArgs const&);
private:
    winrt::Microsoft::UI::Xaml::Window window_{ nullptr };
};
} // namespace winrt::OSFM::ServerApp::implementation

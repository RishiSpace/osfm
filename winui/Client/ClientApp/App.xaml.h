#pragma once
// App.g.h (cppwinrt, from App.idl) declares implementation::App_base;
// App.xaml.g.h (XAML compiler) declares AppT deriving from it.
// The .g.h MUST come first (mirrors MainWindow pattern below).
#include "App.g.h"
#include "App.xaml.g.h"
#include <winrt/Microsoft.UI.Xaml.h>

namespace winrt::OSFM::ClientApp::implementation {
struct App : AppT<App> {
    App();
    void OnLaunched(winrt::Microsoft::UI::Xaml::LaunchActivatedEventArgs const&);
private:
    winrt::Microsoft::UI::Xaml::Window window_{ nullptr };
};
} // namespace winrt::OSFM::ClientApp::implementation

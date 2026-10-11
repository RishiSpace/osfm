#pragma once
// App.xaml.g.h (XAML compiler) fully defines AppT from the Application root
// in App.xaml. No App.idl exists and no winrt/ projection is needed.
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

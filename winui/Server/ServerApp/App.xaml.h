#pragma once
// App_base comes from the MIDL projection (App.idl -> winrt/OSFM.ServerApp.h);
// App.xaml.g.h (XAML compiler) derives AppT from it. Projection first.
#include "winrt/OSFM.ServerApp.h"
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

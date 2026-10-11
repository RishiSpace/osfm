#pragma once
// App_base comes from the MIDL projection (App.idl -> winrt/OSFM.ClientApp.h);
// App.xaml.g.h (XAML compiler) derives AppT from it. Projection first.
#include "winrt/OSFM.ClientApp.h"
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

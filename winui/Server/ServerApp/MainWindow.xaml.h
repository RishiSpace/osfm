#pragma once
// MainWindow.g.h (cppwinrt, from MainWindow.idl) declares
// implementation::MainWindow_base; MainWindow.xaml.g.h derives from it.
// The .g.h MUST come first.
#include "MainWindow.g.h"
#include "MainWindow.xaml.g.h"
#include "TcpServer.h"
#include <winrt/Microsoft.UI.Xaml.h>
#include <winrt/Microsoft.UI.Xaml.Controls.h>
#include <memory>

namespace winrt::OSFM::ServerApp::implementation {

struct MainWindow : MainWindowT<MainWindow> {
    MainWindow();

    void OnInstallBtn(winrt::Windows::Foundation::IInspectable const&,
                      winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnUninstallBtn(winrt::Windows::Foundation::IInspectable const&,
                        winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnFixBtn(winrt::Windows::Foundation::IInspectable const&,
                  winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnNetOn(winrt::Windows::Foundation::IInspectable const&,
                 winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnNetShare(winrt::Windows::Foundation::IInspectable const&,
                    winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnNetOff(winrt::Windows::Foundation::IInspectable const&,
                  winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnAddUser(winrt::Windows::Foundation::IInspectable const&,
                   winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnDelUser(winrt::Windows::Foundation::IInspectable const&,
                   winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnPsSend(winrt::Windows::Foundation::IInspectable const&,
                  winrt::Microsoft::UI::Xaml::RoutedEventArgs const&);
    void OnClientDoubleTapped(winrt::Windows::Foundation::IInspectable const&,
                              winrt::Microsoft::UI::Xaml::Input::DoubleTappedRoutedEventArgs const&);

private:
    void RefreshClients();
    void AppendLog(std::string line);
    std::unique_ptr<osfm::server::TcpServer> server_;
};

} // namespace winrt::OSFM::ServerApp::implementation

// Activation factory: required by the XAML compiler even for same-project
// activation (matches the VS Blank App template verbatim).
namespace winrt::OSFM::ServerApp::factory_implementation {
struct MainWindow : MainWindowT<MainWindow, implementation::MainWindow> {
};
} // namespace winrt::OSFM::ServerApp::factory_implementation

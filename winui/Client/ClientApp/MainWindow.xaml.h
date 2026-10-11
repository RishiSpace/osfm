#pragma once
// MainWindow.g.h (cppwinrt, from MainWindow.idl) declares
// implementation::MainWindow_base; MainWindow.xaml.g.h derives from it.
// The .g.h MUST come first.
#include "MainWindow.g.h"
#include "MainWindow.xaml.g.h"
#include <winrt/Microsoft.UI.Xaml.h>
#include <memory>
#include "ClientEngine.h"

namespace winrt::OSFM::ClientApp::implementation {
struct MainWindow : MainWindowT<MainWindow> {
    MainWindow();
private:
    std::unique_ptr<osfm::client::ClientEngine> engine_;
};
} // namespace winrt::OSFM::ClientApp::implementation

// Activation factory: required by the XAML compiler even for same-project
// activation (matches the VS Blank App template verbatim).
namespace winrt::OSFM::ClientApp::factory_implementation {
struct MainWindow : MainWindowT<MainWindow, implementation::MainWindow> {
};
} // namespace winrt::OSFM::ClientApp::factory_implementation

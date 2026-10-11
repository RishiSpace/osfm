// MainWindow.xaml.cpp — code-behind (compiled on Windows with C++/WinRT).
// Wires CommandBar buttons to TcpServer::Broadcast, prompts for users/winget,
// and routes engine callbacks to the UI thread via DispatcherQueue.
// Dialog flows are detached coroutines: blocking .get() on ShowAsync() would
// deadlock the UI thread, so handlers spawn fire-and-forget lambdas instead.

#include "pch.h"
#include "MainWindow.xaml.h"
#if __has_include("MainWindow.g.cpp")
#include "MainWindow.g.cpp"
#endif

#include "Logger.h"
#include "NetUtils.h"
#include "OsfmProtocol.h"
#include "Privilege.h"
#include "ProcessUtils.h"
#include "Toast.h"
#include "Winget.h"

#include <filesystem>

using namespace winrt;
using namespace Microsoft::UI::Xaml;
using namespace Microsoft::UI::Xaml::Controls;

namespace winrt::OSFM::ServerApp::implementation {

static hstring W(const std::string& s) { return hstring(osfm::net::ToWide(s)); }
static std::string N(const hstring& h) { return osfm::net::ToNarrow(std::wstring(h)); }

MainWindow::MainWindow() {
    InitializeComponent();

    osfm::log::Init(L"OSFM-Server.log");
    osfm::log::SetUiSink([this](const std::string& line) {
        DispatcherQueue().TryEnqueue([this, line] { AppendLog(line); });
    });

    if (!osfm::priv::IsElevated())
        osfm::priv::EnsureElevated(L"--server"); // privileged ops need admin

    osfm::priv::EnsureFirewallRule(osfm::kPort);
    osfm::priv::EnsureSmbShare(L"osfm-temp", osfm::priv::DefaultTempDir());

    osfm::server::Callbacks cb;
    auto dq = DispatcherQueue();
    cb.onConnect = [this, dq](const osfm::server::ClientInfo&) {
        dq.TryEnqueue([this] { RefreshClients(); });
    };
    cb.onDisconnect = [this, dq](const std::string&) {
        dq.TryEnqueue([this] { RefreshClients(); });
    };
    cb.onAck = [this, dq](const std::string&, bool) {
        dq.TryEnqueue([this] {
            AckBar().Maximum(static_cast<double>(server_->Clients().size()));
            AckBar().Value(static_cast<double>(server_->Completed()));
            RefreshClients();
        });
    };
    cb.onLog = [](const std::string& line) { osfm::log::Info(line); };

    server_ = std::make_unique<osfm::server::TcpServer>(
        osfm::kPort, osfm::net::GetHostname(), std::move(cb));
    if (!server_->Start())
        osfm::toast::Show(L"OSFM Control Centre", L"Port 12345 busy — another server is running.");

    InstallBtn().Click({ this, &MainWindow::OnInstallBtn });
    UninstallBtn().Click({ this, &MainWindow::OnUninstallBtn });
    FixBtn().Click({ this, &MainWindow::OnFixBtn });
    NetOnBtn().Click({ this, &MainWindow::OnNetOn });
    NetShareBtn().Click({ this, &MainWindow::OnNetShare });
    NetOffBtn().Click({ this, &MainWindow::OnNetOff });
    AddUserBtn().Click({ this, &MainWindow::OnAddUser });
    DelUserBtn().Click({ this, &MainWindow::OnDelUser });
    PsSendBtn().Click({ this, &MainWindow::OnPsSend });
    ClientsView().DoubleTapped({ this, &MainWindow::OnClientDoubleTapped });
}

void MainWindow::RefreshClients() {
    ClientsView().Items().Clear();
    for (auto& c : server_->Clients()) {
        StackPanel row;
        row.Orientation(Orientation::Horizontal);
        TextBlock name;
        name.Text(W(c.display + "  [" + c.address + "]  " + c.status));
        row.Children().Append(name);
        ClientsView().Items().Append(row);
    }
}

void MainWindow::AppendLog(std::string line) {
    LogBox().Text(LogBox().Text() + W(line + "\n"));
}

void MainWindow::OnInstallBtn(IInspectable const&, RoutedEventArgs const&) {
    // winget search dialog -> download to osfm-temp -> FILE_PATH + INSTALL.
    auto strong = get_strong();
    [strong, this]() -> winrt::fire_and_forget {
        TextBox q;
        q.PlaceholderText(L"Search winget, e.g. vlc");
        ContentDialog dlg;
        dlg.Title(box_value(L"Install software"));
        dlg.Content(q);
        dlg.PrimaryButtonText(L"Search & deploy");
        dlg.CloseButtonText(L"Cancel");
        dlg.XamlRoot(this->Content().XamlRoot());
        if (co_await dlg.ShowAsync() != ContentDialogResult::Primary) co_return;
        auto pkgs = osfm::winget::Search(N(q.Text()));
        auto host = osfm::net::GetHostname();
        auto staging = osfm::priv::DefaultTempDir();
        for (auto& p : pkgs) {
            std::filesystem::path dir =
                std::filesystem::path{ staging } / osfm::net::ToWide(p.id);
            osfm::winget::Download(p.id, dir.wstring());
            auto unc = osfm::net::ToNarrow(
                osfm::priv::UncTempPath(osfm::net::ToWide(host),
                                        osfm::net::ToWide(p.id)));
            server_->Broadcast(std::string(osfm::kFilePathPrefix) + unc);
        }
        if (!pkgs.empty()) server_->Broadcast(osfm::kInstall);
        osfm::toast::Show(L"Install Apps", L"App path sent to all clients.");
    }();
}

void MainWindow::OnUninstallBtn(IInspectable const&, RoutedEventArgs const&) {
    auto strong = get_strong();
    [strong, this]() -> winrt::fire_and_forget {
        TextBox id;
        id.PlaceholderText(L"winget id, e.g. VideoLAN.VLC");
        ContentDialog dlg;
        dlg.Title(box_value(L"Uninstall software"));
        dlg.Content(id);
        dlg.PrimaryButtonText(L"Uninstall everywhere");
        dlg.CloseButtonText(L"Cancel");
        dlg.XamlRoot(this->Content().XamlRoot());
        if (co_await dlg.ShowAsync() != ContentDialogResult::Primary) co_return;
        server_->Broadcast(std::string(osfm::kPsPrefix) +
                           osfm::winget::UninstallCommand(N(id.Text())));
    }();
}

void MainWindow::OnFixBtn(IInspectable const&, RoutedEventArgs const&) {
    server_->Broadcast(osfm::kFix); // clients run sfc + DISM, reply 200 OK
}

void MainWindow::OnNetOn(IInspectable const&, RoutedEventArgs const&) {
    server_->Broadcast(std::string(osfm::kPsPrefix) + osfm::priv::DnsResetCommand());
}
void MainWindow::OnNetShare(IInspectable const&, RoutedEventArgs const&) {
    server_->Broadcast(std::string(osfm::kSetDnsPrefix) + osfm::net::GetHostname());
    osfm::toast::Show(L"Internet Sharing", L"Shared internet with all clients.");
}
void MainWindow::OnNetOff(IInspectable const&, RoutedEventArgs const&) {
    server_->Broadcast(std::string(osfm::kPsPrefix) + osfm::priv::DnsDisableCommand());
}

void MainWindow::OnAddUser(IInspectable const&, RoutedEventArgs const&) {
    auto strong = get_strong();
    [strong, this]() -> winrt::fire_and_forget {
        TextBox u;
        u.PlaceholderText(L"username");
        PasswordBox p;
        p.PlaceholderText(L"password");
        StackPanel sp;
        sp.Children().Append(u);
        sp.Children().Append(p);
        ContentDialog d;
        d.Title(box_value(L"Create user"));
        d.Content(sp);
        d.PrimaryButtonText(L"OK");
        d.CloseButtonText(L"Cancel");
        d.XamlRoot(this->Content().XamlRoot());
        if (co_await d.ShowAsync() != ContentDialogResult::Primary) co_return;
        auto user = N(u.Text());
        auto pass = N(p.Password());
        // pass is Restricted: used once in the command string, never logged.
        if (user.empty() || pass.empty()) co_return;
        server_->Broadcast(std::string(osfm::kPsPrefix) +
                           osfm::priv::CreateUserCommand(user, pass));
        server_->Broadcast(std::string(osfm::kToastCPrefix) + user);
        osfm::toast::Show(L"User Management", L"User created.");
    }();
}

void MainWindow::OnDelUser(IInspectable const&, RoutedEventArgs const&) {
    auto strong = get_strong();
    [strong, this]() -> winrt::fire_and_forget {
        TextBox u;
        u.PlaceholderText(L"username");
        ContentDialog d;
        d.Title(box_value(L"Delete user"));
        d.Content(u);
        d.PrimaryButtonText(L"Delete everywhere");
        d.CloseButtonText(L"Cancel");
        d.XamlRoot(this->Content().XamlRoot());
        if (co_await d.ShowAsync() != ContentDialogResult::Primary) co_return;
        auto user = N(u.Text());
        if (user.empty()) co_return;
        server_->Broadcast(std::string(osfm::kPsPrefix) +
                           osfm::priv::DeleteUserCommand(user));
        server_->Broadcast(std::string(osfm::kToastDPrefix) + user);
        osfm::toast::Show(L"User Management", L"User deleted.");
    }();
}

void MainWindow::OnPsSend(IInspectable const&, RoutedEventArgs const&) {
    auto cmd = N(PsBox().Text());
    if (cmd.empty()) return;
    server_->Broadcast(std::string(osfm::kPsPrefix) + cmd);
    osfm::toast::Show(L"PowerShell Execution", L"Script sent to all connected clients.");
}

void MainWindow::OnClientDoubleTapped(IInspectable const&,
    winrt::Microsoft::UI::Xaml::Input::DoubleTappedRoutedEventArgs const&) {
    auto i = ClientsView().SelectedIndex();
    if (i < 0) return;
    auto clients = server_->Clients();
    if (static_cast<size_t>(i) < clients.size())
        osfm::proc::OpenRdp(osfm::net::ToWide(clients[i].display)); // mstsc /v:
}

} // namespace winrt::OSFM::ServerApp::implementation

#Requires -RunAsAdministrator
# Opens OSFM-Net port 12345 (TCP+UDP, private profile) for server + clients.
param([int]$Port = 12345)
foreach ($proto in 'TCP','UDP') {
  $name = "OSFM-Net $proto $Port"
  if (-not (Get-NetFirewallRule -DisplayName $name -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $name -Direction Inbound -Protocol $proto `
      -LocalPort $Port -Action Allow -Profile Private | Out-Null
  }
}
Write-Host "Firewall open for TCP+UDP $Port (Private)."

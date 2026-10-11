#Requires -RunAsAdministrator
# Shares %ProgramData%\OSFM\osfm-temp as \\HOST\osfm-temp (parity with ensure_temp_folder_shared).
$dir = Join-Path $env:ProgramData 'OSFM\osfm-temp'
if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
if (-not (Get-SmbShare -Name 'osfm-temp' -ErrorAction SilentlyContinue)) {
  New-SmbShare -Name 'osfm-temp' -Path $dir -FullAccess Everyone | Out-Null
}
Write-Host "Shared $dir as \\$env:COMPUTERNAME\osfm-temp"

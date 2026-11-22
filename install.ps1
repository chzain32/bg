#Requires -RunAsAdministrator
$ErrorActionPreference = "Stop"
$dst = "C:\ProgramData\RuntimeBroker"

$build = [int](Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion").CurrentBuildNumber
if ($build -lt 26100) { throw "Windows build $build < 26100. Upgrade to 11 24H2 first." }

$pyw = (Get-Command pythonw).Source
if (-not $pyw) { throw "pythonw missing. Install Python 3.11 x64 and tick Add to PATH." }
& (Get-Command python).Source -m pip install --quiet --disable-pip-version-check -r "$PSScriptRoot\req.lock"

New-Item -ItemType Directory -Force "$dst\agent","$dst\client" | Out-Null
Copy-Item "$PSScriptRoot\agent\*.py","$PSScriptRoot\agent\*.pyw" "$dst\agent" -Force
Copy-Item "$PSScriptRoot\client\*" "$dst\client" -Force
Copy-Item "$PSScriptRoot\verify.py" $dst -Force

$tok = -join ((48..57)+(65..90)+(97..122) | Get-Random -Count 40 | ForEach-Object {[char]$_})
$env:GHOST_TOKEN = $tok
Set-Content "$env:LOCALAPPDATA\ghost.token" $tok

$act = New-ScheduledTaskAction -Execute $pyw -Argument "`"$dst\agent\run.pyw`""
$set = New-ScheduledTaskSettingsSet -Hidden -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries -RestartCount 999 `
        -RestartInterval (New-TimeSpan -Minutes 1) -ExecutionTimeLimit 0
Register-ScheduledTask -TaskName "RuntimeBroker" -Action $act `
  -Trigger (New-ScheduledTaskTrigger -AtLogOn) `
  -Principal (New-ScheduledTaskPrincipal -UserId $env:USERNAME -RunLevel Highest) `
  -Settings $set -Force | Out-Null

Remove-NetFirewallRule -DisplayName "blueghost" -ErrorAction SilentlyContinue
New-NetFirewallRule -DisplayName "blueghost" -Direction Inbound -Protocol TCP `
  -LocalPort 8731 -RemoteAddress 100.64.0.0/10 -Action Allow | Out-Null

powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /setactive SCHEME_MIN
(Get-WmiObject -Class BatteryStatus -Namespace root\wmi -ErrorAction SilentlyContinue) | Out-Null

Start-ScheduledTask -TaskName "RuntimeBroker"
Start-Sleep 4
Write-Host ""
Write-Host "TOKEN:" -ForegroundColor Cyan
Write-Host $tok -ForegroundColor Yellow
Write-Host ""
Write-Host "Open: http://127.0.0.1:8731/ on this machine to test locally." -ForegroundColor Gray
#Requires -RunAsAdministrator
Unregister-ScheduledTask -TaskName "RuntimeBroker" -Confirm:$false -ErrorAction SilentlyContinue
Remove-NetFirewallRule -DisplayName "blueghost" -ErrorAction SilentlyContinue
Stop-Process -Name pythonw -Force -ErrorAction SilentlyContinue
Remove-Item "C:\ProgramData\RuntimeBroker" -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "removed"
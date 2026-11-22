#Requires -RunAsAdministrator
if (-not $env:DWSHARE_KEY) { throw "set `$env:DWSHARE_KEY first" }
Invoke-WebRequest "https://www.dwservice.net/download/dwagent_x64.exe" -OutFile "$env:TEMP\dw.exe"
Start-Process "$env:TEMP\dw.exe" -ArgumentList "-silent","key=$env:DWSHARE_KEY" -Wait
Get-Service dwagent | Select-Object Name,Status
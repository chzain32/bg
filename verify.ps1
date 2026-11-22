#Requires -RunAsAdministrator
$py = (Get-Command python).Source
Push-Location "C:\ProgramData\RuntimeBroker"
& $py verify.py
$rc = $LASTEXITCODE
Pop-Location
Write-Host ""
Write-Host ("DRILL " + $(if ($rc -eq 0) { "PASS" } else { "FAIL - do not sit" })) -ForegroundColor $(if ($rc -eq 0) { "Green" } else { "Red" })
exit $rc
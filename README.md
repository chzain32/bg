# blueghost

Target: Windows 11 24H2+. Operator: any browser. Cost: $0.

## Target install
1. Python 3.11 x64, tick Add to PATH.
2. Elevated PowerShell:
   Set-ExecutionPolicy Bypass -Scope Process -Force
   irm https://raw.githubusercontent.com/<you>/blueghost/main/install.ps1 | iex
3. Copy the printed token.
4. Elevated PowerShell: .\verify.ps1   -> must say PASS

## Transport
winget install -e --id Tailscale.Tailscale
tailscale up
tailscale ip -4          # gives 100.x.y.z

## Operate
Browser -> http://100.x.y.z:8731/  (or wss://<tunnel>/ after
cloudflared tunnel --url http://127.0.0.1:8731)
Paste token, CONNECT, press FULL.

## Keys
1-5 answer · n next · p previous · drag to highlight · Q slider for bandwidth

## Tuning (drill only)
panel.html top block: CHOICE.x, CHOICE.y[], NEXTBTN, PREVBTN.
Set them from a practice test at 100% scaling, commit, re-drill.
# demo-api.ps1 - one-shot live demo of the secure API (for lab screenshots)
# Usage (PowerShell, in the project root):
#   .\demo-api.ps1          (PowerShell prompt in this folder; do NOT use -File, it fails on [ ] in the path)
# It starts Flask, runs all security checks, then stops Flask.

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $here
$py = Join-Path $here ".venv\Scripts\python.exe"
$base = "http://127.0.0.1:5000"
$d = Join-Path $here "demo"

# .NET ProcessStartInfo treats the bracketed path [HDU...] literally
# (Start-Process / -File would treat [ ] as wildcards).
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $py
$psi.Arguments = "app.py"
$psi.WorkingDirectory = $here
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
Write-Host "Starting Flask server ..." -ForegroundColor Cyan
$job = [System.Diagnostics.Process]::Start($psi)
Start-Sleep -Seconds 4

function Header($t) {
  Write-Host ""
  Write-Host ("===== " + $t + " =====") -ForegroundColor Yellow
}
function Show($line) { Write-Host $line }

Header "1. LOGIN correct (admin/Admin123!) -> expect 200 + JWT"
Show ("HTTP " + (curl.exe -s -o NUL -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json" -w "%{http_code}"))
Show "Response body (token):"
curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json" | ForEach-Object { Show $_ }

Header "2. LOGIN wrong password -> expect 401"
Show ("HTTP " + (curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_wrong.json" -w "%{http_code}" -o "$env:TEMP\o2.txt"))
Get-Content "$env:TEMP\o2.txt" | ForEach-Object { Show $_ }

Header "3. SQL INJECTION login (admin' OR '1'='1) -> expect 401, blocked"
Show ("HTTP " + (curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_sqli.json" -w "%{http_code}" -o "$env:TEMP\o3.txt"))
Get-Content "$env:TEMP\o3.txt" | ForEach-Object { Show $_ }

Header "4. GET /api/data WITHOUT token -> expect 401"
Show ("HTTP " + (curl.exe -s "$base/api/data" -w "%{http_code}" -o "$env:TEMP\o4.txt"))
Get-Content "$env:TEMP\o4.txt" | ForEach-Object { Show $_ }

$resp = curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json"
$token = ($resp | ConvertFrom-Json).token

Header "5. GET /api/data WITH valid token -> expect 200 + user list"
Show ("HTTP " + (curl.exe -s "$base/api/data" -H "Authorization: Bearer $token" -w "%{http_code}" -o "$env:TEMP\o5.txt"))
Get-Content "$env:TEMP\o5.txt" | ForEach-Object { Show $_ }

Header "6. POST /api/posts with XSS payload -> expect 201, content auto-escaped"
Show ("HTTP " + (curl.exe -s -X POST "$base/api/posts" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d "@$d\p_xss.json" -w "%{http_code}" -o "$env:TEMP\o6.txt"))
Get-Content "$env:TEMP\o6.txt" | ForEach-Object { Show $_ }

Write-Host ""
Write-Host "Stopping Flask server ..." -ForegroundColor Cyan
Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
Write-Host "Done. Screenshot this window for the API / security evidence." -ForegroundColor Green

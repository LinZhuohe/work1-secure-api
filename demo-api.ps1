# demo-api.ps1 - one-shot live demo of the secure API (for lab screenshots)
# Usage (PowerShell, in the project root):
#   powershell -ExecutionPolicy Bypass -File demo-api.ps1
# It starts Flask, runs all security checks, then stops Flask.

$ErrorActionPreference = "Continue"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -LiteralPath $here
$py = Join-Path $here ".venv\Scripts\python.exe"
$base = "http://127.0.0.1:5000"
$d = Join-Path $here "demo"

Write-Host "Starting Flask server ..." -ForegroundColor Cyan
# Use .NET ProcessStartInfo so the bracketed path [HDU...] is treated literally
# (Start-Process/-File would treat [ ] as wildcards).
$psi = New-Object System.Diagnostics.ProcessStartInfo
$psi.FileName = $py
$psi.Arguments = "app.py"
$psi.WorkingDirectory = $here
$psi.UseShellExecute = $false
$psi.CreateNoWindow = $true
$job = [System.Diagnostics.Process]::Start($psi)
Start-Sleep -Seconds 4

function Show($title, $sb) {
  Write-Host ""
  Write-Host ("===== " + $title + " =====") -ForegroundColor Yellow
  & $sb
}

Show "1. LOGIN correct (admin/Admin123!) -> expect 200 + JWT" {
  curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json"
  Write-Host ""
  Write-Host ("HTTP " + (curl.exe -s -o NUL -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json" -w "%{http_code}")) -ForegroundColor Green
}

Show "2. LOGIN wrong password -> expect 401" {
  curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_wrong.json" -w "`nHTTP %{http_code}`n"
}

Show "3. SQL INJECTION login (admin' OR '1'='1) -> expect 401, blocked" {
  curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_sqli.json" -w "`nHTTP %{http_code}`n"
}

Show "4. GET /api/data WITHOUT token -> expect 401" {
  curl.exe -s "$base/api/data" -w "`nHTTP %{http_code}`n"
}

$resp = curl.exe -s -X POST "$base/auth/login" -H "Content-Type: application/json" -d "@$d\p_login.json"
$token = ($resp | ConvertFrom-Json).token

Show "5. GET /api/data WITH valid token -> expect 200 + user list" {
  curl.exe -s "$base/api/data" -H "Authorization: Bearer $token" -w "`nHTTP %{http_code}`n"
}

Show "6. POST /api/posts with XSS payload -> expect 201, content auto-escaped" {
  curl.exe -s -X POST "$base/api/posts" -H "Authorization: Bearer $token" -H "Content-Type: application/json" -d "@$d\p_xss.json" -w "`nHTTP %{http_code}`n"
}

Write-Host ""
Write-Host "Stopping Flask server ..." -ForegroundColor Cyan
Stop-Process -Id $job.Id -Force -ErrorAction SilentlyContinue
Write-Host "Done. You can screenshot this window for the API/security evidence." -ForegroundColor Green

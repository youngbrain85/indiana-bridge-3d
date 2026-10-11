$ErrorActionPreference = 'Stop'
$appRoot = $PSScriptRoot
$appUrl = 'http://127.0.0.1:8766'
$existing = $null
try { $existing = Invoke-RestMethod -Uri "$appUrl/api/health" -TimeoutSec 2 } catch {}
if ($existing.app -ne 'indiana-bridge-manager') {
    if (Get-NetTCPConnection -LocalPort 8766 -State Listen -ErrorAction SilentlyContinue) {
        throw 'Port 8766 is already used by another application. Run server.py --port with another port.'
    }
    $pythonPath = Join-Path $appRoot '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $pythonPath)) { $pythonPath = (Get-Command python -ErrorAction Stop).Source }
    $serverPath = Join-Path $appRoot 'server.py'
    $logsPath = Join-Path $appRoot 'data'
    New-Item -ItemType Directory -Path $logsPath -Force | Out-Null
    $process = Start-Process -FilePath $pythonPath -ArgumentList @('-X', 'utf8', ('"' + $serverPath + '"')) -WorkingDirectory $appRoot -WindowStyle Hidden -RedirectStandardOutput (Join-Path $logsPath 'server.stdout.log') -RedirectStandardError (Join-Path $logsPath 'server.stderr.log') -PassThru
    $process.Id | Set-Content -LiteralPath (Join-Path $logsPath 'server.pid')
    $started = $false
    for ($attempt = 0; $attempt -lt 40; $attempt++) {
        Start-Sleep -Milliseconds 250
        try {
            $health = Invoke-RestMethod -Uri "$appUrl/api/health" -TimeoutSec 1
            if ($health.app -eq 'indiana-bridge-manager') { $started = $true; break }
        } catch {}
    }
    if (-not $started) { throw 'The local server did not start. See data/server.stderr.log.' }
}
Start-Process $appUrl

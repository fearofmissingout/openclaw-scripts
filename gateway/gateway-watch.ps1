# OpenClaw Gateway Auto-Restart Script
# Run as: powershell -ExecutionPolicy Bypass -File gateway-watch.ps1

$GatewayUrl = "http://127.0.0.1:18789/health"
$CheckInterval = 30  # seconds
$LogFile = "$env:USERPROFILE\.openclaw\logs\gateway-watch.log"

# Create log directory if not exists
$logDir = Split-Path $LogFile -Parent
if (!(Test-Path $logDir)) {
    New-Item -ItemType Directory -Path $logDir -Force | Out-Null
}

function Write-Log {
    param([string]$Message)
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    "$timestamp - $Message" | Out-File -FilePath $LogFile -Append -Encoding utf8
    Write-Host "$timestamp - $Message"
}

function Test-Gateway {
    try {
        $response = Invoke-WebRequest -Uri $GatewayUrl -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}

function Start-Gateway {
    Write-Log "Gateway not responding, starting..."
    
    # Kill existing node processes for openclaw
    Get-Process -Name "node" -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    
    # Start gateway in background
    Start-Process -FilePath "openclaw" -ArgumentList "gateway","run" -WindowStyle Hidden
    
    Write-Log "Gateway restart initiated"
}

# Main loop
Write-Log "Gateway Watcher Started"

while ($true) {
    if (Test-Gateway) {
        Write-Log "Gateway OK"
    } else {
        Write-Log "Gateway DOWN, restarting..."
        Start-Gateway
    }
    
    Start-Sleep -Seconds $CheckInterval
}

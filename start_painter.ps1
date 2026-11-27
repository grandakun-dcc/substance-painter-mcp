param(
    [int]$ReadyTimeout = 120,
    [switch]$KeepAlive,
    [string]$PainterExe = 'C:\Program Files\Adobe\Adobe Substance 3D Painter\Adobe Substance 3D Painter.exe',
    [string]$WorkerRoot = (Join-Path $env:LOCALAPPDATA 'MCP\SubstancePainter-MCP\state')
)

$ErrorActionPreference = 'Stop'
$connectionFile = Join-Path $WorkerRoot 'connection.json'
function Get-WorkerConnection {
    try {
        if (-not (Test-Path $connectionFile)) { return $null }
        $connection = Get-Content -Raw $connectionFile | ConvertFrom-Json
        if ($connection.host -ne '127.0.0.1') { return $null }
        $workerProcess = Get-Process -Id $connection.pid -ErrorAction Stop
        if ($workerProcess.Path -ne $PainterExe) { return $null }
        $health = Invoke-RestMethod -Uri "http://127.0.0.1:$($connection.port)/health" `
            -Headers @{ Authorization = "Bearer $($connection.token)" } -TimeoutSec 2
        if ($health.closed -or $health.runtime_id -ne $connection.runtime_id) { return $null }
        return $connection
    } catch { return $null }
}
try {
    $connection = Get-WorkerConnection
    if ($null -ne $connection) {
        Write-Output "SubstancePainter-MCP worker is ready on port $($connection.port) (PID $($connection.pid))."
        exit 0
    }
    $pythonRoot = Join-Path $WorkerRoot 'python'
    $startup = Join-Path $pythonRoot 'startup'
    if (-not (Test-Path (Join-Path $startup 'substancepainter_startup.py'))) {
        throw 'Run install.ps1 before starting the worker.'
    }
    $env:PAINTER_MCP_HOME = $WorkerRoot
    $env:PAINTER_MCP_CONNECTION = $connectionFile
    $env:SUBSTANCE_PAINTER_PLUGINS_PATH = $pythonRoot
    $env:PYTHONDONTWRITEBYTECODE = '1'
    $startedPainter = Start-Process -FilePath $PainterExe -ArgumentList @(
        '--no-default-project', '--disable-version-checking'
    ) -WindowStyle Minimized -PassThru
    $deadline = [DateTime]::UtcNow.AddSeconds($ReadyTimeout)
    while ([DateTime]::UtcNow -lt $deadline) {
        $connection = Get-WorkerConnection
        if ($null -ne $connection) {
            if ($connection.pid -ne $startedPainter.Id) { throw 'Connection belongs to a different process.' }
            Write-Output "SubstancePainter-MCP worker is ready on port $($connection.port) (PID $($connection.pid))."
            if ($KeepAlive) { $startedPainter.WaitForExit() }
            exit 0
        }
        if ($startedPainter.HasExited) { throw 'Worker exited before its MCP plugin became available.' }
        Start-Sleep -Milliseconds 500
    }
    throw "Worker was not ready within $ReadyTimeout seconds."
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}

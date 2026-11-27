param([string]$Python = 'python')

$ErrorActionPreference = 'Stop'
$installRoot = Join-Path $env:LOCALAPPDATA 'MCP\SubstancePainter-MCP'
$pythonExe = Join-Path $installRoot '.venv\Scripts\python.exe'
$env:PYTHONDONTWRITEBYTECODE = '1'
if (-not (Test-Path $pythonExe)) {
    & $Python -m venv (Join-Path $installRoot '.venv')
    if ($LASTEXITCODE -ne 0) { throw 'Could not create the independent Python environment.' }
}
& $pythonExe -m pip install $PSScriptRoot --index-url 'https://pypi.tuna.tsinghua.edu.cn/simple'
if ($LASTEXITCODE -ne 0) { throw 'Could not install SubstancePainter-MCP.' }
$env:PAINTER_MCP_HOME = Join-Path $installRoot 'state'
$env:PAINTER_MCP_CONNECTION = Join-Path $env:PAINTER_MCP_HOME 'connection.json'
& $pythonExe -m substancepainter_mcp install
if ($LASTEXITCODE -ne 0) { throw 'Plugin installation did not complete.' }
$config = @{
    mcpServers = @{
        'SubstancePainter-MCP' = @{
            command = $pythonExe
            args = @('-m', 'substancepainter_mcp', 'serve')
            env = @{
                PAINTER_MCP_HOME = $env:PAINTER_MCP_HOME
                PAINTER_MCP_CONNECTION = $env:PAINTER_MCP_CONNECTION
                PYTHONDONTWRITEBYTECODE = '1'
            }
        }
    }
}
$config | ConvertTo-Json -Depth 6 | Set-Content (Join-Path $PSScriptRoot 'mcp.json') -Encoding UTF8
Write-Output 'Installed. Run start_painter.ps1, then import mcp.json into your MCP client.'

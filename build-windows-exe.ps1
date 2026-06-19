param(
    [string]$Name = "15-Puzzle-AI"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ProjectRoot

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

$addData = @(
    "app.py;.",
    "core;core",
    "algorithms;algorithms",
    "ui;ui",
    "app-screenshot.png;.",
    "puzzle-v2.png;."
)

$args = @(
    "--noconfirm",
    "--clean",
    "--name", $Name,
    "--windowed",
    "--collect-data", "streamlit",
    "--copy-metadata", "streamlit",
    "--copy-metadata", "altair",
    "--copy-metadata", "pydeck",
    "--hidden-import", "streamlit.web.bootstrap",
    "--hidden-import", "watchdog.observers.winapi",
    "--hidden-import", "webview",
    "--hidden-import", "webview.platforms.edgechromium",
    "--exclude-module", "matplotlib",
    "--exclude-module", "scipy",
    "--exclude-module", "plotly",
    "--exclude-module", "pytest",
    "--exclude-module", "pyarrow.tests",
    "--exclude-module", "pandas.tests"
)

foreach ($item in $addData) {
    $args += @("--add-data", $item)
}

$args += "desktop_app.py"

python -m PyInstaller @args

$exePath = Join-Path $ProjectRoot "dist\$Name\$Name.exe"
if (!(Test-Path $exePath)) {
    throw "Build finished but EXE was not found at $exePath"
}

Write-Host "Built EXE: $exePath"

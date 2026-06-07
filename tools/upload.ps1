# Upload een experiment + de shared utilities naar de Pico via mpremote.
#
# Gebruik: .\tools\upload.ps1 experiments\01_weerstation
#
# Het script kopieert:
#   - experiments/NN_naam/main.py       -> :main.py
#   - experiments/NN_naam/<submap>/*.py -> :<submap>/*.py
#   - shared/*.py                       -> :shared/*.py
#
# Vereist: mpremote (uv tool install mpremote).

param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$ExperimentDir
)

$MainPy = Join-Path $ExperimentDir 'main.py'

if (-not (Test-Path $MainPy)) {
    Write-Error "Geen main.py gevonden in $ExperimentDir"
    exit 1
}

if (-not (Get-Command mpremote -ErrorAction SilentlyContinue)) {
    Write-Error "mpremote niet gevonden. Installeer met: uv tool install mpremote"
    exit 1
}

Write-Host "Aanmaken van :shared/ op de Pico (genegeerd als die al bestaat)"
mpremote mkdir shared

Write-Host "Uploaden van shared modules"
Get-ChildItem -Path 'shared' -Filter '*.py' -File | ForEach-Object {
    Write-Host "  cp $($_.FullName) -> :shared/$($_.Name)"
    mpremote cp $_.FullName ":shared/$($_.Name)"
}

# Upload submappen van het experiment (bijv. sensors/, output/, handlers/)
Get-ChildItem -Path $ExperimentDir -Directory | ForEach-Object {
    $submap = $_.Name
    $bestanden = Get-ChildItem -Path $_.FullName -Filter '*.py' -File
    if ($bestanden.Count -gt 0) {
        Write-Host "Aanmaken van :$submap/ op de Pico"
        mpremote mkdir $submap
        $bestanden | ForEach-Object {
            Write-Host "  cp $($_.FullName) -> :$submap/$($_.Name)"
            mpremote cp $_.FullName ":$submap/$($_.Name)"
        }
    }
}

# Upload losse .py bestanden in de experimentmap (niet main.py, config.py of test_*.py)
Get-ChildItem -Path $ExperimentDir -Filter '*.py' -File |
    Where-Object { $_.Name -notin @('main.py', 'config.py') -and $_.Name -notlike 'test_*' } |
    ForEach-Object {
        Write-Host "  cp $($_.FullName) -> :$($_.Name)"
        mpremote cp $_.FullName ":$($_.Name)"
    }

Write-Host "Uploaden van $MainPy -> :main.py"
mpremote cp $MainPy ':main.py'

Write-Host "Klaar. Start REPL met: mpremote"

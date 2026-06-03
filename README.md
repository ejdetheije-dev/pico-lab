# Pico Lab

Experimenteer-lab rond de Raspberry Pi Pico 2W. Korte, op zichzelf staande
MicroPython-experimenten met sensoren en actuatoren uit het Freenove Ultimate
Starter Kit.

## Vereisten

- Raspberry Pi Pico 2W met MicroPython firmware
- Freenove Ultimate Starter Kit (sensoren, breadboard, jumper wires)
- Windows-laptop met Python 3, `uv` en `mpremote`

## Snelstart

1. Installeer `mpremote`:

   ```powershell
   uv tool install mpremote
   ```

2. Sluit de Pico 2W aan via USB. Controleer de COM-poort:

   ```powershell
   mpremote connect list
   ```

3. Upload een experiment:

   ```powershell
   .\tools\upload.ps1 experiments\01_weerstation
   ```

4. Open de REPL om output te zien:

   ```powershell
   mpremote
   ```

## Mappen

- `experiments/` — één map per experiment, met `main.py` en een eigen README
- `shared/` — herbruikbare modules (WiFi, logger, LCD helper)
- `tools/` — upload- en hulpscripts
- `plan.md` — overzicht en volgorde van experimenten

## Volgende stap

Lees `plan.md` voor de aanbevolen volgorde en `CLAUDE.md` voor pinout en
codeerstijl.

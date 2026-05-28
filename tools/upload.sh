#!/usr/bin/env bash
# Upload een experiment + de shared utilities naar de Pico via mpremote.
#
# Gebruik: ./tools/upload.sh experiments/01_weerstation
#
# Het script kopieert:
#   - experiments/NN_naam/main.py  -> :main.py
#   - shared/*.py                  -> :shared/*.py
#
# Vereist: mpremote (`pip install mpremote`).

set -euo pipefail

if [ $# -ne 1 ]; then
    echo "Gebruik: $0 <experiment-pad>" >&2
    echo "Voorbeeld: $0 experiments/01_weerstation" >&2
    exit 1
fi

EXPERIMENT_DIR="$1"
MAIN_PY="${EXPERIMENT_DIR}/main.py"

if [ ! -f "$MAIN_PY" ]; then
    echo "Geen main.py gevonden in ${EXPERIMENT_DIR}" >&2
    exit 1
fi

if ! command -v mpremote >/dev/null 2>&1; then
    echo "mpremote niet gevonden. Installeer met: pip install mpremote" >&2
    exit 1
fi

echo "Aanmaken van :shared/ op de Pico (negeer fout als die al bestaat)"
mpremote mkdir shared || true

echo "Uploaden van shared modules"
for f in shared/*.py; do
    [ -f "$f" ] || continue
    name="$(basename "$f")"
    echo "  cp $f -> :shared/$name"
    mpremote cp "$f" ":shared/$name"
done

echo "Uploaden van $MAIN_PY -> :main.py"
mpremote cp "$MAIN_PY" :main.py

echo "Klaar. Start REPL met: mpremote"

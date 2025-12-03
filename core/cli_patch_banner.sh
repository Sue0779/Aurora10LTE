#!/bin/bash

set -e

CLI=~/.aurora/core/cli.py
BACKUP="$CLI.bak_banner_$(date +%Y%m%d_%H%M%S)"

echo "[1] Tworzę backup: $BACKUP"
cp "$CLI" "$BACKUP"

echo "[2] Patchuję banner startowy..."

# Zamiana starej linijki print(...) na nowy minimalny banner
sed -i '
s/print(f"{CYAN}AuroraOS – powłoka CLI (dwuwyrazowe komendy aktywne){RESET}")/print(f"{CYAN}Aurora 10 LTE — modułowa powłoka AI{RESET}")/
' "$CLI"

echo "[3] Patch zakończony."
echo "Uruchom ponownie: aurora"

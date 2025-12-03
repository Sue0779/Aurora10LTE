#!/bin/bash

set -e

CLI=~/.aurora/core/cli.py
BACKUP="$CLI.bak_prompt_$(date +%Y%m%d_%H%M%S)"

echo "[1] Tworzę backup: $BACKUP"
cp "$CLI" "$BACKUP"

echo "[2] Patchuję plik cli.py – dynamiczny prompt..."

# Wstawiamy nową funkcję _prompt()
# oraz poprawiamy linię input(...)
sed -i '
/def main()/i \
def _prompt(ctx):\
    profile = "default"\
    if isinstance(ctx.profile, dict) and "name" in ctx.profile:\
        profile = ctx.profile["name"]\
    return f"{YELLOW}[{profile}] aurora>{RESET} "


# Podmiana input(...) na input(_prompt(ctx))
s/input("aurora> ")/input(_prompt(ctx))/g
' "$CLI"

echo "[3] Patch zakończony."
echo "Uruchom ponownie: aurora"

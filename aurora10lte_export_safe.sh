#!/usr/bin/env bash
set -euo pipefail

AURORA_SRC="$HOME/.aurora"
REPO="$HOME/projekty/Aurora10LTE_repo"

echo "[SAFE MODE] Eksporter Aurora10LTE"
echo "Źródło (tylko odczyt): $AURORA_SRC"
echo "Repo docelowe:         $REPO"
echo

# 0) Weryfikacja, czy katalog źródłowy istnieje
if [[ ! -d "$AURORA_SRC" ]]; then
    echo "[BŁĄD] Brak katalogu ~/.aurora — przerwano."
    exit 1
fi

# 1) Czyścimy REPO, ale NIE ruszamy ~/.aurora
echo "[1] Czyszczę repo (TYLKO repo)..."
rm -rf "$REPO/core" \
       "$REPO/plugins" \
       "$REPO/installer"

mkdir -p "$REPO"

# 2) Kopiujemy core (bez .bak, bez .pyc)
echo "[2] Kopiuję core/ (bez kopii zapasowych)..."
rsync -av --exclude='*.bak*' --exclude='__pycache__' \
    "$AURORA_SRC/core/" "$REPO/core/"

# 3) Kopiujemy plugins (również bez .bak)
echo "[3] Kopiuję plugins/ (bez kopii zapasowych)..."
rsync -av --exclude='*.bak*' --exclude='__pycache__' \
    "$AURORA_SRC/plugins/" "$REPO/plugins/"

# 4) Tworzymy minimalistyczny installer (TYLKO w repo)
echo "[4] Tworzę installer/setup.sh..."
mkdir -p "$REPO/installer"

cat > "$REPO/installer/setup.sh" <<EOT
#!/usr/bin/env bash
set -e

echo "Instalator Aurora10LTE"
TARGET="\$HOME/.aurora"
mkdir -p "\$TARGET"

echo "Kopiuję core/..."
cp -r ./core "\$TARGET/"

echo "Kopiuję plugins/..."
cp -r ./plugins "\$TARGET/"

echo "Gotowe!"
EOT

chmod +x "$REPO/installer/setup.sh"

echo
echo "[ZAKOŃCZONE] Eksport 100% BEZPIECZNY. ~/.aurora NIE zostało dotknięte."

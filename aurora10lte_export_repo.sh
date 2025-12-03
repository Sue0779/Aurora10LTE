#!/usr/bin/env bash
set -euo pipefail

# =========================================
# Aurora 10 LTE – eksport frameworku + pluginów do repo Git
# ŹRÓDŁO: ~/.aurora
# CEL:    ./ (katalog repo, z którego odpalasz skrypt)
# =========================================

AURORA_SRC="$HOME/.aurora"
REPO_ROOT="$(pwd)"

echo "[1] Źródło Aurory:   $AURORA_SRC"
echo "[2] Katalog repo:    $REPO_ROOT"

if [ ! -d "$AURORA_SRC/core" ] || [ ! -d "$AURORA_SRC/plugins" ]; then
  echo "[FATAL] Nie znajduję core/ albo plugins/ w \$HOME/.aurora – przerwane."
  exit 1
fi

echo "[3] Czyścimy repo z poprzednich źródeł (core/, plugins/, installer/, docs/)..."
rm -rf \
  "$REPO_ROOT/core" \
  "$REPO_ROOT/plugins" \
  "$REPO_ROOT/installer" \
  "$REPO_ROOT/docs" \
  "$REPO_ROOT/.venv" \
  "$REPO_ROOT/venv"

mkdir -p "$REPO_ROOT/core"
mkdir -p "$REPO_ROOT/plugins"
mkdir -p "$REPO_ROOT/installer"
mkdir -p "$REPO_ROOT/docs"

# -----------------------------------------
# 4) Kopiowanie core (bez śmieci)
# -----------------------------------------
echo "[4] Kopiuję core/ z ~/.aurora/core → repo/core..."
rsync -av \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*~' \
  "$AURORA_SRC/core/" "$REPO_ROOT/core/"

# -----------------------------------------
# 5) Kopiowanie plugins (bez śmieci)
# -----------------------------------------
echo "[5] Kopiuję plugins/ z ~/.aurora/plugins → repo/plugins..."
rsync -av \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '*~' \
  --exclude 'plugins_backup_*' \
  "$AURORA_SRC/plugins/" "$REPO_ROOT/plugins/"

# -----------------------------------------
# 6) Minimalny installer (setup.sh)
# -----------------------------------------
INSTALLER="$REPO_ROOT/installer/setup.sh"

echo "[6] Tworzę minimalny installer: installer/setup.sh..."
cat > "$INSTALLER" << 'EOS'
#!/usr/bin/env bash
set -euo pipefail

AURORA_ROOT="$HOME/.aurora"

echo "[Aurora10LTE setup] Instaluję do: $AURORA_ROOT"

mkdir -p "$AURORA_ROOT/core"
mkdir -p "$AURORA_ROOT/plugins"
mkdir -p "$AURORA_ROOT/logs"
mkdir -p "$AURORA_ROOT/profiles"

# Kopia core
rsync -av \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  ./core/ "$AURORA_ROOT/core/"

# Kopia plugins
rsync -av \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  ./plugins/ "$AURORA_ROOT/plugins/"

# Profil domyślny
if [ ! -f "$AURORA_ROOT/profiles/default.profile.json" ]; then
  cat > "$AURORA_ROOT/profiles/default.profile.json" << 'EOP'
{
  "name": "default",
  "model": "gpt-5.1"
}
EOP
fi

echo "[Aurora10LTE setup] Gotowe. Uruchom:  aurora"
EOS

chmod +x "$INSTALLER"

# -----------------------------------------
# 7) Czyszczenie lokalnych śmieci
# -----------------------------------------
echo "[7] Czyszczę ewentualne śmieci w repo..."
find "$REPO_ROOT" -name '__pycache__' -type d -prune -exec rm -rf {} + || true
find "$REPO_ROOT" -name '*.pyc' -type f -delete || true

# -----------------------------------------
# 8) Podsumowanie
# -----------------------------------------
echo
echo "[OK] Aurora10LTE – eksport zakończony."
echo "Sprawdź diff:  git status && git diff"
echo "Jeśli wygląda OK:"
echo "  git add core plugins installer"
echo "  git commit -m \"Aurora10LTE: initial public export\""
echo "  git push"

#!/usr/bin/env bash
set -e

echo "Instalator Aurora10LTE"
TARGET="$HOME/.aurora"
mkdir -p "$TARGET"

echo "Kopiuję core/..."
cp -r ./core "$TARGET/"

echo "Kopiuję plugins/..."
cp -r ./plugins "$TARGET/"

echo "Gotowe!"

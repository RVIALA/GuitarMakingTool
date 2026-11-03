#!/usr/bin/env sh
set -eu
cd -- "$(dirname -- "$0")"
if [ "$(uname -s)" != Linux ]; then
  printf '%s\n' 'Ce lanceur est destiné à Linux / This installer is for Linux.'
  exit 1
fi
# System libraries are installed only when explicitly requested.
if [ "${1:-}" = '--system' ]; then
  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y python3 python3-venv libglu1-mesa libxft2 libxrender1 libxcursor1 libxinerama1
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y python3 mesa-libGLU libXft libXrender libXcursor libXinerama
  else
    printf '%s\n' 'Distribution : voir INSTALLATION.md / see INSTALLATION.md.'
    exit 1
  fi
fi
sh ./lancer_gmt.sh --install-only

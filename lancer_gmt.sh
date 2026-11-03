#!/usr/bin/env sh
# Select a supported Python without changing the system Python.
set -eu
cd -- "$(dirname -- "$0")"
for candidate in python3 python3.15 python3.14 python3.13 python3.12 python3.11 python; do
  if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; sys.exit(not (sys.version_info[:2] >= (3,11)))' 2>/dev/null; then
    exec "$candidate" start.py "$@"
  fi
done
printf '%s\n' 'Python 3.11+ (64 bits) requis / required.' 'Installer Python puis relancer / Install Python then retry.' 'Voir INSTALLATION.md / See INSTALLATION.md.'
exit 1

#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
sh ./lancer_gmt.sh --install-only
result=$?
printf '\nInstallation terminée (code %s) / Installation finished (code %s).\n' "$result" "$result"
read -r -p 'Entrée pour fermer / Enter to close… '
exit "$result"

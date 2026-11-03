#!/bin/bash
cd -- "$(dirname -- "$0")" || exit 1
sh ./lancer_gmt.sh "$@"
result=$?
if [ "$result" -ne 0 ]; then
  printf '\nÉchec du lancement / Launch failed. Voir / See INSTALLATION.md\n'
  read -r -p 'Entrée pour fermer / Enter to close… '
fi
exit "$result"

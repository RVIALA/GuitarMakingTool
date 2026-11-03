# Vérifications / Verification — 3 November 2026

Auteur / Author: Romain VIALA.

| Vérification / Check | Résultat / Result |
|---|---|
| Chromium, quatre interfaces, FR/EN, 320/390/768 px | PASS |
| WebKit Linux, quatre interfaces, FR/EN, 320/390/768 px | PASS |
| PickupTool : jeu et export WAV / play and WAV export, Chromium | PASS |
| QuatuorTool : coup d’archet et WAV / bowed note and WAV, Chromium | PASS |
| PickupTool : 50 vérifications moteur/effets/accords / engine/effects/chords | PASS |
| QuatuorTool : énergie, friction, familles / energy, friction, families | PASS |
| ToneWoodTool : cinq tests géométrie/FEM/FEMU/import / five numerical tests | PASS |
| ToneWoodTool : saisie, calcul, WAV importé, exports WAV/CSV/JSON / UI workflow | PASS |
| GMT + ToneWoodTool : exécutables Linux, HTTP et calcul FEM / frozen runtime + FEM | PASS |
| Quatre PDF LaTeX, A4, schémas TikZ, renvois SHA-256 / four manuals and references | PASS |

WebKit Linux audio playback did not complete in this headless environment; audio is not validated on Safari. No real macOS, Windows, iPhone or iPad execution was performed. CI recipes target those desktop systems but are not completed native-platform tests. iOS/iPadOS can host the two static web interfaces through HTTPS; the GMT/ToneWoodTool desktop engines cannot run on iOS. No physical microphone acquisition was tested.

La lecture audio WebKit Linux n’a pas abouti dans cet environnement sans écran ; l’audio Safari reste à valider. Aucun essai sur appareil macOS, Windows, iPhone ou iPad n’a été effectué. Les recettes CI ciblent ces ordinateurs ; elles ne constituent pas des essais réalisés. Les deux interfaces statiques sont destinées à un hébergement HTTPS ; les moteurs desktop GMT/ToneWoodTool ne s’exécutent pas sous iOS. L’acquisition avec un microphone physique n’a pas été testée.

These are implementation and regression checks, not experimental validation of a particular instrument or material. / Ces contrôles ne constituent pas une validation expérimentale d’un instrument ou matériau réel.

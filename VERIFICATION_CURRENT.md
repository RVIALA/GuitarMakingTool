# Vérification de cette révision / Current revision verification

Auteur / Author: **Romain VIALA** — 3 novembre 2026.

Les rapports historiques décrivent la version précédente. Le lancement Chromium de cette révision a été empêché par les restrictions de sockets de l’environnement ; aucun essai navigateur complet, périphérique audio, WebGL réel, macOS ou iOS n’est revendiqué pour cette révision.
Historical reports describe the previous version. Environment socket restrictions prevented Chromium startup for this revision; this revision has no claimed full browser, physical audio, actual WebGL, macOS or iOS test.

Les icônes sont des SVG décoratifs originaux intégrés localement, sans police externe ; les textes FR/EN restent visibles. Syntaxe JavaScript vérifiée. Les PDF ont été compilés depuis LaTeX en A4, contrôlés sans débordement et les renvois vérifiés par empreintes de code.
Icons are original local decorative SVGs, with no external font; FR/EN labels remain visible. JavaScript syntax checked. A4 PDFs were compiled from LaTeX, checked for overflow, with code-reference hashes verified.

- Cinq jeux de points et fichier de pans coupés identiques à GMT 1.6 joint ; code actuel conservé. / Five outline datasets and cutaway file match the supplied GMT 1.6; current application code retained.
- tests/contours.py : six préréglages × quatre pans coupés, dimensions, fermeture, validité, tolérance de simplification, ouvertures, aire, profondeur, symétrie et migration des anciennes sessions — PASS.
- Six presets × four cutaway choices passed geometry checks. No new mesh convergence study or native executable build was run.
- Références et conditions des tracés : PUBLICATION.md. / Outline attribution and conditions: PUBLICATION.md.

English-only manual: docs/manual-en.pdf, source docs/manual-en.tex; rebuild both editions with python docs/build_english.py. Affichage numérique harmonisé : DISPLAY_PRECISION.md. Significant-digit formatting and confidence-interval alignment tests: PASS; display only, engine and export precision unchanged.

3D update: unrestricted rotation, roll, pan, zoom, radius preservation and pointer cleanup: PASS (camera mathematics/DOM boundaries). GMT export readback through pyuff 2.5.8: PASS for datasets 164/2411/2412/55. Capture workflow tests: PASS with recorder/WebGL boundaries mocked; real browser codecs and GPU rendering remain untested in this environment. Quatuor neck mirror and existing interaction checks: PASS.

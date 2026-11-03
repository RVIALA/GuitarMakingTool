# Modes, images et vidéos / Modes, images and videos

**Romain VIALA**

## Français

- Les viewers utilisent une rotation libre : glisser gauche ou un doigt pour tourner, molette/pincement pour zoomer, glisser droit ou Maj pour déplacer. Deux doigts : déplacement, pincement et rotation dans le plan. Aucun axe vertical n’est imposé. Réinitialiser restaure la vue de départ.
- Atelier : afficher la 3D, choisir un élément (vue courante, table, fond, éclisses, barrages, chevalet) puis Image 3D PNG. Aucune résolution EF n’est nécessaire pour cette image de géométrie.
- Maillage et modes : choisir le mode et l’élément, régler amplitude, palette, transparence et caméra, puis Image PNG ou Vidéo du mode. Vidéo silencieuse de 6 s, animation ralentie pour la visualisation ; elle ne représente pas la fréquence temporelle réelle. MP4 ou WebM selon les codecs disponibles. Le navigateur doit rester actif pendant la capture. Une modification du mode interrompt l’export au lieu de mélanger les résultats.
- UNV et UFF contiennent les mêmes données, avec deux extensions usuelles. Boutons disponibles après calcul du modèle courant. Il s’agit des modes mécaniques secs EF d’origine ; les retouches virtuelles de fréquence/amortissement des FRF, le couplage acoustique et les vecteurs de correction résiduelle sont exclus.
- Données Universal ASCII : 164 unités SI, 2411 nœuds (XYZ en m), 2412 peau triangulée de visualisation, 55 modes réels à trois composantes. Tous les nœuds solides et leurs vecteurs sont inclus, avec identifiants locaux 1..N cohérents entre géométrie et modes. La peau triangulée ne remplace pas le maillage volumique TET10.
- Vecteurs normalisés en masse, masse modale 1 ; fréquences Hz et amortissement visqueux équivalent zeta=eta/2. La norme E13.5 des enregistrements 55 impose six chiffres significatifs dans ce format. Choisir NPZ pour conserver la précision numérique complète ; MSH/VTK restent disponibles pour le maillage.

## English

- Free trackball viewers: left drag or one finger rotates, wheel/pinch zooms, right drag or Shift pans. Two fingers support pan, pinch and in-plane roll. There is no locked world-up axis. Reset restores the initial view.
- Workshop: enable 3D, select a part (current view, top, back, ribs, braces, bridge), then 3D PNG image. This geometry image needs no FE solve.
- Mesh and modes: select a mode and part, adjust amplitude, palette, transparency and camera, then PNG image or Mode video. Videos are silent, six seconds long, with slow visual animation rather than physical-time oscillation. MP4 or WebM depends on available codecs. Keep the browser active. Changing the mode aborts capture instead of mixing results.
- UNV and UFF contain identical data under two customary extensions. Export requires the solved current model. These are original dry structural FE modes; virtual FRF frequency/damping edits, acoustic coupling and residual correction vectors are excluded.
- ASCII Universal datasets: 164 SI units, 2411 nodes (XYZ in metres), 2412 triangular visualization skin, 55 real three-component modes. All solid nodes and modal vectors are retained, with consistent local IDs 1..N. The triangular skin is not the TET10 volume FE mesh.
- Mass-normalized vectors, modal mass 1; frequencies in Hz and equivalent viscous damping ratio zeta=eta/2. Standard E13.5 dataset-55 records retain six significant digits. Choose NPZ for full numerical precision; MSH/VTK remain available for mesh interchange.

## Format references

https://www.svibs.com/resources/ARTeMIS_Modal_Help_v7/UFF%20Data%20Set%20Number%2055.html

https://pyuff.readthedocs.io/en/latest/_modules/pyuff/datasets/dataset_2411.html

https://pyuff.readthedocs.io/en/latest/_modules/pyuff/datasets/dataset_2412.html

The writer is original GMT code. pyuff is used only for independent test readback, and is not a runtime dependency. Native application import testing in commercial modal-analysis software remains to be performed.

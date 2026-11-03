# GMT

**Romain VIALA** · 1.10.0 · [Français](README.md) | [English](README_EN.md)

Géométrie de guitare acoustique, calcul FEM, mobilité au chevalet et synthèse sonore.

Pour les utilisateurs novices, distribuer une archive desktop créée par le workflow GitHub Actions. Elle inclut Python et les bibliothèques de calcul : l’utilisateur extrait le dossier complet et lance le programme, qui ouvre le navigateur local. Le navigateur seul sur GitHub Pages ne peut pas exécuter ce backend. iOS/iPadOS ne lancent pas ces exécutables ; un portage ou serveur hébergé séparé serait nécessaire.

## Démarrer

Télécharger la release adaptée : Windows x64, Linux x64, macOS Apple Silicon ou macOS Intel. Conserver tous les fichiers ensemble. Windows : lancer le `.exe` ; Linux : `chmod +x Launch.sh` puis `./Launch.sh` ; macOS : ouvrir `Launch.command`. Ces builds ne sont pas signés/notariés. Ne pas désactiver globalement Gatekeeper.

Depuis les sources : Python 3.12 recommandé ; `python -m venv .venv`, activer cet environnement, puis `python -m pip install -r requirements.txt` et `python server.py`. Les lanceurs Linux et macOS automatisent la préparation de l’environnement lorsqu’elle est nécessaire.

Gmsh sous Debian/Ubuntu nécessite `sudo apt install libglu1-mesa libxft2 libxrender1 libxinerama1`.

## Documentation

- [Equations / Équations (PDF)](docs/manual.pdf), [LaTeX](docs/manual.tex).
- [Code tree / Arborescence](docs/tree.tikz), [dependencies / dépendances](docs/dependencies.tikz).
- [Credits / Crédits](CREDITS.md), [sources](SOURCES.md), [author / auteur](AUTHORS.md).
- `python docs/verify_references.py`: checks source hashes and line references / vérifie les empreintes et renvois.

## Compatibilité

Les rapports de la version précédente couvrent Chromium et WebKit sous Linux ; ils ne remplacent pas des essais physiques Safari/macOS/iOS. Les recettes desktop ciblent Windows, Linux, Mac Intel et Apple Silicon ; seule l’exécution Linux peut être vérifiée ici.

## Licences

Licence de l’application : GPL v3 ou ultérieure, voir LICENSE.txt. Les composants tiers conservent leurs licences. / Application: GPL v3 or later, see LICENSE.txt; dependencies keep their licenses.

Lire les notices de tous les composants avant publication ; l’audit des sources ne garantit pas les droits des tiers.

[Tests et limites / Tests and limits](VERIFICATION.md).

## Contours / Outline rights

Contours GMT 1.6 rétablis, application actuelle conservée. Droits de redistribution à vérifier avant publication publique : [PUBLICATION.md](PUBLICATION.md). / GMT 1.6 contours restored in the current application. Review [PUBLICATION.md](PUBLICATION.md) before public redistribution.

[Nouveautés / What changed](RELEASE_FR_EN.md) · [Vérification de cette révision / Current checks](VERIFICATION_CURRENT.md).

[English-only equations PDF](docs/manual-en.pdf) · [Bilingual equations PDF](docs/manual.pdf) · [Display precision / Chiffres significatifs](DISPLAY_PRECISION.md).

[Images, vidéos et exports UNV/UFF / Images, videos and UNV/UFF exports](MODAL_EXPORTS_FR_EN.md).

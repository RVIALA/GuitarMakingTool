# GMT

**Romain VIALA** · 1.10.0 · [Français](README.md) | [English](README_EN.md)

Acoustic guitar geometry, FEM, bridge mobility and sound synthesis.

For novice users, distribute a desktop archive built by the GitHub Actions workflow. It includes Python and calculation libraries: extract the whole folder and launch the executable, which opens a local browser. GitHub Pages alone cannot execute this backend. iOS/iPadOS cannot run these executables; a separate port or hosted server would be needed.

## Start

Download the matching release: Windows x64, Linux x64, macOS Apple Silicon or macOS Intel. Keep all files together. Windows: run the `.exe`; Linux: `chmod +x Launch.sh` then `./Launch.sh`; macOS: open `Launch.command`. Builds are not signed/notarized in this repository. Do not disable Gatekeeper globally.

Developer/source fallback: Python 3.12 recommended; `python -m venv .venv`, activate it, then `python -m pip install -r requirements.txt` and `python server.py`. Linux and macOS launchers automate environment preparation where supplied.

Gmsh on Debian/Ubuntu needs `sudo apt install libglu1-mesa libxft2 libxrender1 libxinerama1`.

## Documentation

- [Equations / Équations (PDF)](docs/manual.pdf), [LaTeX](docs/manual.tex).
- [Code tree / Arborescence](docs/tree.tikz), [dependencies / dépendances](docs/dependencies.tikz).
- [Credits / Crédits](CREDITS.md), [sources](SOURCES.md), [author / auteur](AUTHORS.md).
- `python docs/verify_references.py`: checks source hashes and line references / vérifie les empreintes et renvois.

## Compatibility

Browser tests cover Chromium and WebKit under Linux. This is not physical Safari/macOS/iOS testing. Desktop build recipes target Windows, Linux, Mac Intel and Apple Silicon; only Linux execution can be checked here.

## Licensing

Licence de l’application : GPL v3 ou ultérieure, voir LICENSE.txt. Les composants tiers conservent leurs licences. / Application: GPL v3 or later, see LICENSE.txt; dependencies keep their licenses.

Read all component notices before publication; the source audit is not a guarantee of third-party rights.

[Tests et limites / Tests and limits](VERIFICATION.md).

## Contours / Outline rights

Contours GMT 1.6 rétablis, application actuelle conservée. Droits de redistribution à vérifier avant publication publique : [PUBLICATION.md](PUBLICATION.md). / GMT 1.6 contours restored in the current application. Review [PUBLICATION.md](PUBLICATION.md) before public redistribution.

[Nouveautés / What changed](RELEASE_FR_EN.md) · [Vérification de cette révision / Current checks](VERIFICATION_CURRENT.md).

[English-only equations PDF](docs/manual-en.pdf) · [Bilingual equations PDF](docs/manual.pdf) · [Display precision / Chiffres significatifs](DISPLAY_PRECISION.md).

[Images, vidéos et exports UNV/UFF / Images, videos and UNV/UFF exports](MODAL_EXPORTS_FR_EN.md).

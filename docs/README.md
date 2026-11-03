# Documentation FR / EN

`manual.pdf` est compilé depuis `manual.tex`. / `manual.pdf` is compiled from `manual.tex`.

Recompiler le PDF : / Recompile PDF:

```sh
cd docs
pdflatex -halt-on-error manual.tex
pdflatex -halt-on-error manual.tex
```

Après modification du code, les renvois doivent être recalculés : / After code changes, refresh references:

```sh
python docs/build_manual.py docs/equations.json
python docs/verify_references.py
```

Requires Python 3.11+ for documentation generation only, and TeX Live with LaTeX, Latin Modern, babel, amsmath, geometry, microtype, hyperref and TikZ. No Python is required to use PickupTool or QuatuorTool.

`tree.tikz` et `dependencies.tikz` sont éditables ; les fichiers `*-standalone.tex` compilent les schémas seuls. / Editable TikZ diagrams have standalone A4 wrappers.

`equations.csv` et `source-map.json` indiquent les positions dans le code de cette version. / Equation indexes refer to this exact source version. `manifest.csv` at repository root lists all distributed files.

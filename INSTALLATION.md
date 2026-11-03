# GMT 1.8.0 — Python récent / Recent Python

Python **3.11 à 3.14, CPython 64 bits standard** : utilisation directe. Python **3.15 et ultérieur**, ou édition free-threaded : le lanceur réutilise un environnement compatible existant, cherche un Python compatible installé, puis en prépare un privé en Python 3.13 avec uv si nécessaire. Le téléchargement initial nécessite Internet. Python système n’est pas remplacé. Les versions futures ne sont pas déclarées compatibles nativement avec le moteur scientifique.

Décompresser dans un nouveau dossier accessible en écriture. Windows : `Lancer_GMT.bat`. macOS : `bash Lancer_GMT.command`. Linux : `sh lancer_gmt.sh`.

Pour imposer un environnement privé compatible :

```sh
python start.py --managed-python --install-only
```

Sous macOS/Linux, utiliser `python3` si nécessaire. En cas d’ancien environnement inutilisable, celui-ci est conservé dans `.venv.previous-*`. Les environnements et téléchargements locaux ne doivent pas être publiés sur GitHub. Une installation réseau interrompue est réessayée au prochain lancement ; le marqueur de réussite n’est écrit qu’après import des dépendances et initialisation Gmsh réussis. Les bibliothèques natives Linux restent nécessaires (voir ci-dessous). Les autres systèmes/architectures sans paquets binaires ne sont pas garantis.

**English:** standard 64-bit CPython 3.11–3.14 can run the engine directly. With 3.15 or later, or a free-threaded build, the launcher reuses or finds a compatible interpreter, otherwise downloads a private Python 3.13 using uv. Initial setup needs Internet; the system Python is unchanged. Future versions are not claimed to run the numerical engine natively. `--managed-python --install-only` forces the private runtime. Broken environments are retained under `.venv.previous-*`.

---

# Installation détaillée / Detailed setup

## Français

Décompresser **tout** le dossier GMT dans un emplacement où vous pouvez écrire. Ne pas lancer depuis l’archive. Python **64 bits 3.11, 3.12, 3.13 ou 3.14** est requis. Les lanceurs privilégient une version compatible disponible. La première installation nécessite Internet ; l’usage est ensuite local.

### Linux

Ouvrir un terminal dans le dossier GMT :

```sh
sh installer_linux.sh --system
sh lancer_gmt.sh
```

L’option `--system` installe les bibliothèques natives via `sudo` sur Debian/Ubuntu (apt) ou Fedora (dnf), puis les dépendances Python dans `.venv`. Le système peut demander votre mot de passe administrateur. Si les bibliothèques système sont déjà installées, utiliser simplement `sh installer_linux.sh`, sans sudo. Si la version Python de la distribution n’est pas compatible, installer Python 3.11–3.14 avant de relancer.

Autres distributions : installer Python compatible, pip/venv et les bibliothèques GLU, Xft, Xrender, Xcursor et Xinerama avec le gestionnaire de paquets, puis lancer `sh installer_linux.sh`.

### macOS

Installer Python 3.11–3.14 depuis https://www.python.org/downloads/macos/ (installateur universal2, adapté aux Mac Intel et Apple Silicon). Dans Terminal, depuis le dossier GMT :

```sh
bash Installer_GMT.command
bash Lancer_GMT.command
```

Pour le double-clic Finder, si nécessaire :

```sh
chmod +x Installer_GMT.command Lancer_GMT.command lancer_gmt.sh
```

Puis ouvrir `Installer_GMT.command` une fois et `Lancer_GMT.command` aux lancements suivants. Si macOS demande une autorisation, vérifier la provenance de l’archive avant d’autoriser son ouverture dans les réglages de sécurité. Ne pas désactiver globalement les protections du système. Si pip ne trouve pas de paquet adapté, vérifier la version et l’architecture de Python indiquées dans le terminal ; éviter de mélanger une installation Intel et ARM.

### Windows

Installer Python 3.11–3.14 64 bits, puis ouvrir `Lancer_GMT.bat`.

### Utilisation et dépannage

Le navigateur ouvre http://127.0.0.1:8768. Garder le terminal ouvert ; **Ctrl+C** arrête le serveur. L’installation des paquets n’est répétée que si `requirements.txt` change ou si `.venv` est supprimé. `python3 start.py --install-only` installe et vérifie sans démarrer le serveur. Ne pas lancer `start.py` avec sudo.

- Port occupé : `sh lancer_gmt.sh --port 8770` (macOS : `bash Lancer_GMT.command --port 8770`).
- Navigateur non ouvert : ouvrir l’adresse affichée ; `--no-browser` évite l’ouverture automatique.
- Échec réseau de pip : rétablir l’accès Internet puis relancer l’installateur. Le marqueur de réussite n’est écrit qu’après une installation réussie.
- Module venv absent sur Debian/Ubuntu : installer `python3-venv` (ou le paquet venv correspondant à votre version Python).
- Bibliothèque native manquante sur Linux : relancer `sh installer_linux.sh --system`.
- Changement d’ordinateur ou d’architecture : ne pas copier `.venv` ; extraire l’archive et réinstaller.

## English

Extract the entire GMT folder into a writable directory. Use **64-bit Python 3.11–3.14**. Internet is required for installation; subsequent use is local.

**Linux:** in the GMT folder, run `sh installer_linux.sh --system`, then `sh lancer_gmt.sh`. The optional `--system` flag uses sudo and apt (Debian/Ubuntu) or dnf (Fedora) to install native dependencies. Without it, only the local Python environment is installed. Other distributions need Python with pip/venv plus GLU, Xft, Xrender, Xcursor and Xinerama. Install a compatible Python if the distribution default is outside the supported range.

**macOS:** install Python 3.11–3.14 using the universal2 installer from https://www.python.org/downloads/macos/. In Terminal, run `bash Installer_GMT.command`, then `bash Lancer_GMT.command`. For Finder double-click, run `chmod +x Installer_GMT.command Lancer_GMT.command lancer_gmt.sh` once. Verify the archive’s origin before granting any macOS security prompt. Do not disable system security globally. Use a consistent Python architecture on Apple Silicon.

**Windows:** install 64-bit Python 3.11–3.14 and open `Lancer_GMT.bat`.

Keep the terminal open. Visit http://127.0.0.1:8768 if the browser does not open. Ctrl+C stops the server. Use `--port 8770` for another port or `--no-browser` to avoid automatic browser opening. `--install-only` installs and verifies dependencies without starting the server. Dependencies are reused unless requirements change or `.venv` is removed. Do not run the launcher with sudo, or move a virtual environment between machines. Retry installation after network failures. Native-library failures on supported Linux distributions can be resolved with `sh installer_linux.sh --system`.

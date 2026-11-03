#!/usr/bin/env python3
"""GMT bootstrap: reuse a healthy environment, or provision an isolated runtime."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from backend.version import VERSION

ROOT = Path(__file__).resolve().parent
PROBE = "import json,sys,struct,sysconfig; print(json.dumps([list(sys.version_info[:2]),struct.calcsize('P')*8,sys.implementation.name,bool(sysconfig.get_config_var('Py_GIL_DISABLED'))]))"


def supported(info):
    version, bits, implementation, free_threaded = info
    return (3, 11) <= tuple(version) <= (3, 14) and bits == 64 and implementation == 'cpython' and not free_threaded


def probe(python):
    try:
        result = subprocess.run([str(python), '-c', PROBE], capture_output=True, text=True, timeout=20)
        return json.loads(result.stdout) if result.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def usable(python):
    info = probe(python)
    return info is not None and supported(info)


def choose_python():
    candidates = [sys.executable]
    candidates += [shutil.which(name) for name in ('python3.14', 'python3.13', 'python3.12', 'python3.11', 'python3', 'python')]
    if os.name == 'nt' and shutil.which('py'):
        for version in ('3.14', '3.13', '3.12', '3.11'):
            result = subprocess.run(['py', '-' + version, '-c', 'import sys; print(sys.executable)'], capture_output=True, text=True)
            if result.returncode == 0:
                candidates.append(result.stdout.strip())
    for candidate in dict.fromkeys(candidates):
        if candidate and usable(candidate):
            return str(Path(candidate).resolve())
    return None


def managed_python():
    """Use uv to install regular CPython 3.13 locally, without changing PATH."""
    runtime = ROOT / '.gmt-runtime'
    runtime.mkdir(exist_ok=True)
    environment = os.environ.copy()
    environment.update(UV_PYTHON_INSTALL_DIR=str(runtime / 'python'), UV_PYTHON_BIN_DIR=str(runtime / 'bin'), UV_PYTHON_INSTALL_BIN='0')
    uv = shutil.which('uv')
    if uv:
        command = [uv]
    else:
        bootstrap = runtime / 'bootstrap'
        python = bootstrap / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
        if probe(python) is None:
            archive_environment(bootstrap)
            subprocess.check_call([str(Path(sys.executable).resolve()), '-m', 'venv', str(bootstrap)])
        command = [str(python), '-m', 'uv']
        check = subprocess.run(command + ['--version'], capture_output=True)
        if check.returncode:
            subprocess.check_call([str(python), '-m', 'pip', 'install', '--only-binary=:all:', '--disable-pip-version-check', 'uv'])
    print('GMT — Préparation de Python 3.13 privé / Preparing private Python 3.13 (Internet)', flush=True)
    subprocess.check_call(command + ['python', 'install', '3.13'], env=environment)
    found = subprocess.check_output(command + ['python', 'find', '--managed-python', '3.13'], env=environment, text=True).strip()
    if not usable(found):
        raise RuntimeError('Python téléchargé incompatible / Downloaded Python is incompatible.')
    return found


def archive_environment(env):
    if env.exists():
        backup = env.with_name(env.name + '.previous-' + str(time.time_ns()))
        env.rename(backup)
        print('GMT — Ancien environnement conservé / Previous environment retained: ' + backup.name, flush=True)


def dependencies_ok(python):
    return subprocess.run([str(python), '-c', 'import numpy,scipy,shapely,gmsh; gmsh.initialize(); gmsh.finalize()'], capture_output=True, text=True)


def main(args=None):
    args = list(sys.argv[1:] if args is None else args)
    if '--help' in args or '-h' in args:
        print('GMT ' + VERSION + ' — python start.py [--port 8768] [--no-browser] [--install-only] [--managed-python]\nPython 3.11–3.14 direct ; versions plus récentes : environnement privé automatique.\nPython 3.11–3.14 directly; newer versions: automatic private runtime.')
        return 0
    force_managed = '--managed-python' in args
    args = [arg for arg in args if arg != '--managed-python']
    env = ROOT / '.venv'
    python = env / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    requirements = ROOT / 'requirements.txt'
    stamp = env / 'gmt-requirements.sha256'
    signature = hashlib.sha256(requirements.read_bytes()).hexdigest()
    if force_managed or not usable(python):
        selected = managed_python() if force_managed else choose_python()
        if not selected:
            selected = managed_python()
        archive_environment(env)
        print('GMT — Création de l’environnement / Creating environment: ' + selected, flush=True)
        subprocess.check_call([selected, '-m', 'venv', str(env)])
    print('GMT — Python ' + '.'.join(map(str, probe(python)[0])), flush=True)
    if not stamp.exists() or stamp.read_text().strip() != signature:
        print('GMT — Installation des dépendances / Installing dependencies (Internet)', flush=True)
        try:
            subprocess.check_call([str(python), '-m', 'pip', 'install', '--only-binary=:all:', '--disable-pip-version-check', '-r', str(requirements)], cwd=ROOT)
        except subprocess.CalledProcessError as error:
            raise RuntimeError('Installation interrompue. Vérifier Internet et les paquets disponibles pour ce système.\nTry: python start.py --managed-python --install-only\nAucun succès enregistré ; relancer après correction. / Retry after resolving the installation error.') from error
        check = dependencies_ok(python)
        if check.returncode:
            raise RuntimeError(native_error(check.stderr))
        stamp.write_text(signature)
    else:
        check = dependencies_ok(python)
        if check.returncode:
            raise RuntimeError(native_error(check.stderr))
    if '--install-only' in args:
        print('GMT — Installation vérifiée / Installation verified', flush=True)
        return 0
    return subprocess.run([str(python), str(ROOT / 'server.py'), *args], cwd=ROOT).returncode


def native_error(details):
    return ('Dépendance impossible à charger / Cannot load dependency.\n'
            'Linux : sh installer_linux.sh --system\n'
            'Si Python ou le dossier a changé : python start.py --managed-python --install-only\n'
            'Voir INSTALLATION.md / See INSTALLATION.md.\n' + details)


if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as error:
        print('\nGMT — ' + str(error), file=sys.stderr)
        if sys.stdin.isatty():
            input('\nEntrée pour fermer / Enter to close… ')
        sys.exit(1)

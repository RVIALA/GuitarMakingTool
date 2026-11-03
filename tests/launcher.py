"""Regression tests for interpreter selection and successful-install markers."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import start

class LauncherTests(unittest.TestCase):
    def test_versions(self):
        for v in (11,12,13,14): self.assertTrue(start.supported([[3,v],64,'cpython',False]))
        for v in (10,15,16): self.assertFalse(start.supported([[3,v],64,'cpython',False]))
        self.assertFalse(start.supported([[3,14],32,'cpython',False]))
        self.assertFalse(start.supported([[3,14],64,'cpython',True]))
    def test_new_python_selects_installed(self):
        with patch.object(start.sys,'executable','new-python'), patch.object(start.shutil,'which',side_effect=lambda name: name if name=='python3.14' else None), patch.object(start,'usable',side_effect=lambda p:p=='python3.14'):
            self.assertEqual(start.choose_python(),str(Path('python3.14').resolve()))
    def test_no_compatible_interpreter(self):
        with patch.object(start,'usable',return_value=False): self.assertIsNone(start.choose_python())
    def test_bad_probe(self):
        with patch.object(start.subprocess,'run',side_effect=OSError('missing')): self.assertIsNone(start.probe('missing'))
    def test_backup_preserves_files(self):
        with tempfile.TemporaryDirectory() as d:
            env=Path(d)/'.venv';env.mkdir();(env/'sentinel').write_text('keep')
            start.archive_environment(env)
            self.assertFalse(env.exists());self.assertEqual(next(Path(d).glob('.venv.previous-*/sentinel')).read_text(),'keep')
    def run_install(self, ok):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'requirements.txt').write_text('test');env=root/'.venv';env.mkdir()
            stamp=env/'gmt-requirements.sha256'
            with patch.object(start,'ROOT',root),patch.object(start,'usable',return_value=True),patch.object(start,'probe',return_value=[[3,14],64,'cpython',False]),patch.object(start.subprocess,'check_call') as install,patch.object(start,'dependencies_ok',return_value=subprocess.CompletedProcess([],0 if ok else 1,stderr='native failure')):
                if ok:
                    self.assertEqual(start.main(['--install-only']),0);self.assertTrue(stamp.exists())
                    self.assertEqual(start.main(['--install-only']),0);self.assertEqual(install.call_count,1)
                else:
                    with self.assertRaises(RuntimeError): start.main(['--install-only'])
                    self.assertFalse(stamp.exists())
    def test_reuse_no_reinstall(self): self.run_install(True)
    def test_failed_import_no_success_marker(self): self.run_install(False)

if __name__=='__main__': unittest.main()

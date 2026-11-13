import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from build_demo import install_build


class BuildTransactionTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.stage, self.output = self.root / 'stage', self.root / 'site'
        self.stage.mkdir()
        self.output.mkdir()
        (self.stage / 'index.html').write_text('new complete site')
        (self.output / 'index.html').write_text('previous complete site')

    def test_copy_failure_keeps_previous_site(self):
        with patch('build_demo.shutil.copytree', side_effect=OSError('disk full')):
            with self.assertRaisesRegex(OSError, 'disk full'):
                install_build(self.stage, self.output)
        self.assertEqual((self.output / 'index.html').read_text(), 'previous complete site')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['site', 'stage'])

    def test_final_rename_failure_restores_previous_site(self):
        import os
        replace = os.replace
        def fail_install(source, destination):
            if Path(source).name == 'ready':
                raise OSError('rename failed')
            return replace(source, destination)
        with patch('build_demo.os.replace', side_effect=fail_install):
            with self.assertRaisesRegex(OSError, 'rename failed'):
                install_build(self.stage, self.output)
        self.assertEqual((self.output / 'index.html').read_text(), 'previous complete site')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['site', 'stage'])

    def test_completed_install_replaces_whole_site(self):
        (self.output / 'obsolete.json').write_text('old')
        install_build(self.stage, self.output)
        self.assertEqual((self.output / 'index.html').read_text(), 'new complete site')
        self.assertFalse((self.output / 'obsolete.json').exists())
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['site', 'stage'])

"""Exercise token resolution and the generated public artifacts/CLI contract."""
import importlib.util
import json
import re
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('build_qt', ROOT / 'tools/build-qt.py')
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class QtBuildTests(unittest.TestCase):
    def setUp(self):
        self.tokens = json.loads((ROOT / 'project/tokens.json').read_text())

    def test_aliases_follow_theme_and_reject_cycles(self):
        for theme in ('light', 'dark'):
            values = build.resolve_tokens(self.tokens, theme)
            self.assertEqual(values['focus'], values['accent'])
        self.tokens['color']['tokens'].append({'name': 'loop', 'value': '{loop}'})
        with self.assertRaisesRegex(ValueError, 'Cyclic token alias'):
            build.resolve_tokens(self.tokens, 'light')

    def test_css_alpha_becomes_qt_alpha(self):
        self.assertEqual(build.qt_color('rgba(57,135,229,0.16)'), 'rgba(57, 135, 229, 41)')
        self.assertEqual(build.qt_color('#ffffff'), '#ffffff')

    def test_palette_preserves_readable_selection_and_disabled_roles(self):
        for theme in ('light', 'dark'):
            values = build.resolve_tokens(self.tokens, theme)
            palette = build.palette(values)
            for group in ('Active', 'Inactive'):
                self.assertEqual(palette[group]['Highlight'], values['accent'])
                self.assertEqual(palette[group]['HighlightedText'], values['on-accent'])
            self.assertEqual(palette['Disabled']['Text'], values['ink-subtle'])

    def test_button_variants_mirror_web_css(self):
        for theme in ('light', 'dark'):
            values = build.resolve_tokens(self.tokens, theme)
            rules = {}
            for selectors, body in re.findall(r'([^{}]+)\{([^}]*)\}', build.stylesheet(self.tokens, theme)):
                props = dict(line.strip().rstrip(';').split(': ', 1) for line in body.strip().splitlines())
                for selector in selectors.split(','):
                    rules.setdefault(selector.strip(), {}).update(props)
            for widget in ('QPushButton', 'QToolButton'):
                def state(variant, pseudo=''):
                    return rules[f'{widget}[variant="{variant}"]{pseudo}']
                self.assertEqual(state('danger'), dict(background=values['bad'], color='#ffffff', **{'border-color': values['bad']}))
                for pseudo in (':hover', ':pressed', ':checked'):
                    self.assertEqual(state('danger', pseudo), dict(background=values['bad'], color='#ffffff', **{'border-color': values['ink-subtle']}))
                    self.assertEqual(state('ghost', pseudo), dict(background=values['surface'], color=values['ink'], **{'border-color': values['line']}))
                    self.assertEqual(state('primary', pseudo)['background'], values['accent-strong'])
                self.assertEqual(state('ghost'), dict(background='transparent', color=values['ink-muted'], **{'border-color': 'transparent'}))

    def test_cli_generates_checks_and_rejects_stale_artifacts(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / 'tools').mkdir()
            (root / 'project').mkdir()
            shutil.copy(ROOT / 'tools/build-qt.py', root / 'tools')
            shutil.copy(ROOT / 'project/tokens.json', root / 'project')
            command = [sys.executable, str(root / 'tools/build-qt.py')]
            def run(*args):
                return subprocess.run([*command, *args], capture_output=True, text=True)
            self.assertNotEqual(run('--check').returncode, 0)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run('--check').returncode, 0)
            # Generated output is the public byte contract, not implementation text.
            for name, output in build.artifacts(self.tokens).items():
                self.assertEqual((root / 'dist' / name).read_text(), output)
            modified = json.loads((root / 'project/tokens.json').read_text())
            modified['color']['tokens'][0]['value']['light'] = '#112233'
            (root / 'project/tokens.json').write_text(json.dumps(modified))
            before = (root / 'dist/lattice.qss').read_bytes()
            self.assertEqual(run('--check').returncode, 1)
            self.assertEqual((root / 'dist/lattice.qss').read_bytes(), before)
            self.assertEqual(run().returncode, 0)
            self.assertEqual(run('--check').returncode, 0)
            (root / 'dist/lattice-dark.qss').write_text('stale')
            self.assertEqual(run('--check').returncode, 1)


if __name__ == '__main__':
    unittest.main()

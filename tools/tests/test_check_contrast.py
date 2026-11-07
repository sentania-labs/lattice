"""Exercise the WCAG contrast checker against known ratios and the real tokens."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('check_contrast', ROOT / 'tools/check-contrast.py')
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)

# The #1 regression: white on the dark `accent` shipped at 3.64:1.
IN_MEMORY = {
    'color': {
        'themes': [{'id': 'light'}, {'id': 'dark'}],
        'tokens': [
            {'name': 'bg', 'value': {'light': '#f6f7f9', 'dark': '#1b1f24'}},
            {'name': 'surface', 'value': {'light': '#ffffff', 'dark': '#23282f'}},
            {'name': 'surface-sunken', 'value': {'light': '#eef1f5', 'dark': '#2a3038'}},
            {'name': 'ink', 'value': {'light': '#1d2430', 'dark': '#f2f4f7'}},
            {'name': 'ink-muted', 'value': {'light': '#5a6676', 'dark': '#b7bfca'}},
            {'name': 'ink-subtle', 'value': {'light': '#8b95a3', 'dark': '#7f8896'}},
            {'name': 'accent', 'value': {'light': '#1f5fbf', 'dark': '#3987e5'}},
            {'name': 'accent-strong', 'value': {'light': '#1a4fa0', 'dark': '#5a9cec'}},
            {'name': 'on-accent', 'value': {'light': '#ffffff', 'dark': '#0b1220'}},
            {'name': 'link', 'value': {'light': '{accent}', 'dark': '{accent-strong}'}},
            {'name': 'accent-soft', 'value': {'light': '#e8f0fc', 'dark': 'rgba(57,135,229,0.16)'}},
            {'name': 'accent-ink', 'value': {'light': '#12376f', 'dark': '#8fbcf5'}},
            {'name': 'ok-soft', 'value': {'light': '#e6f4ec', 'dark': 'rgba(25,158,112,0.16)'}},
            {'name': 'ok-ink', 'value': {'light': '#14532d', 'dark': '#67c9a2'}},
            {'name': 'warn-soft', 'value': {'light': '#fdf3d8', 'dark': 'rgba(224,164,0,0.09)'}},
            {'name': 'warn-ink', 'value': {'light': '#8a6100', 'dark': '#e0a400'}},
            {'name': 'bad', 'value': {'light': '#a22c1c', 'dark': '#c64e1e'}},
            {'name': 'on-bad', 'value': {'light': '#ffffff', 'dark': '#ffffff'}},
            {'name': 'bad-soft', 'value': {'light': '#fbe9e6', 'dark': 'rgba(217,89,38,0.12)'}},
            {'name': 'bad-ink', 'value': {'light': '#7f1d1d', 'dark': '#d95926'}},
        ],
    },
}


class RatioMathTests(unittest.TestCase):
    def test_black_on_white_is_the_maximum(self):
        self.assertAlmostEqual(check.contrast_ratio('#000000', '#ffffff'), 21.0, places=4)

    def test_same_colour_is_one(self):
        self.assertAlmostEqual(check.contrast_ratio('#3987e5', '#3987e5'), 1.0, places=4)

    def test_white_on_dark_accent_is_the_issue_one_value(self):
        self.assertAlmostEqual(check.contrast_ratio('#ffffff', '#3987e5'), 3.64, places=2)

    def test_ratio_is_symmetric_and_hex_short_forms_agree(self):
        long = check.contrast_ratio('#ffffff', '#1a4fa0')
        self.assertAlmostEqual(check.contrast_ratio('#1a4fa0', '#ffffff'), long, places=6)
        self.assertAlmostEqual(check.contrast_ratio('#fff', '#1a4fa0'), long, places=6)

    def test_alpha_is_flattened_on_the_given_ground(self):
        # The 16%-alpha accent tint flattens on white to about #e8f0fc, so both
        # spellings of the light accent ground read as passing.
        alpha = check.contrast_ratio('#12376f', 'rgba(57,135,229,0.16)', base='#ffffff')
        flat = check.contrast_ratio('#12376f', '#e8f0fc', base='#ffffff')
        self.assertGreater(alpha, 4.5)
        self.assertAlmostEqual(alpha, flat, delta=0.5)
        # The same tint over a dark ground is a different, lower ratio.
        self.assertLess(check.contrast_ratio('#12376f', 'rgba(57,135,229,0.16)', base='#23282f'), 2.0)

    def test_parse_accepts_the_two_forms_tokens_use(self):
        self.assertEqual(check.parse_color('#0b1220'), ((11, 18, 32), 1.0))
        self.assertEqual(check.parse_color('rgba(25,158,112,0.16)'), ((25, 158, 112), 0.16))
        with self.assertRaises(ValueError):
            check.parse_color('nominal')


class PairingTests(unittest.TestCase):
    def test_pairing_list_covers_the_brand_book_table(self):
        documented = {
            ('bg', 'ink'), ('bg', 'ink-muted'),
            ('surface', 'ink'), ('surface', 'ink-muted'), ('surface', 'ink-subtle'),
            ('surface-sunken', 'ink'), ('surface-sunken', 'ink-muted'),
            ('accent', 'on-accent'), ('accent-strong', 'on-accent'),
            ('accent-soft', 'accent-ink'), ('ok-soft', 'ok-ink'),
            ('warn-soft', 'warn-ink'), ('bad-soft', 'bad-ink'),
        }
        self.assertEqual({tuple(p) for p in check.PAIRINGS}, documented)

    def test_every_token_name_in_the_table_resolves(self):
        tokens = json.loads((ROOT / 'project/tokens.json').read_text())
        for theme in ('light', 'dark'):
            values = check.resolve(tokens, theme)
            for ground, ink in check.PAIRINGS:
                with self.subTest(theme=theme, pair=(ground, ink)):
                    self.assertIn(ground, values)
                    self.assertIn(ink, values)

    def test_checks_every_pairing_in_both_themes(self):
        rows = check.check(IN_MEMORY)
        self.assertEqual(len(rows), 2 * (len(check.PAIRINGS) + len(check.EXTRA_TEXT_PAIRINGS)
                                         + len(check.CONTROL_BORDER_PAIRINGS)))
        self.assertEqual({r['theme'] for r in rows}, {'light', 'dark'})
        for row in rows:
            self.assertIsInstance(row['ratio'], float)
            self.assertIsInstance(row['ok'], bool)

    def test_the_minimum_uses_the_unrounded_ratio(self):
        # #6e7978 on white is 4.4976:1, which displays as 4.50 yet fails 4.5.
        boundary = json.loads(json.dumps(IN_MEMORY))
        for token in boundary['color']['tokens']:
            if token['name'] == 'ink-subtle':
                token['value']['light'] = '#6e7978'
        self.assertAlmostEqual(check.contrast_ratio('#6e7978', '#ffffff'),
                               4.4975956603938485, places=9)
        rows = [r for r in check.check(boundary)
                if r['theme'] == 'light' and r['kind'] == 'text'
                and (r['ground'], r['ink']) == ('surface', 'ink-subtle')]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['ratio'], 4.5)          # display is rounded
        self.assertFalse(rows[0]['ok'])                    # the compare is not
        self.assertIn('FAIL', subprocess.run(
            [sys.executable, str(ROOT / 'tools/check-contrast.py'), '--minimum', '4.6'],
            capture_output=True, text=True).stdout or '')

    def test_reports_a_failing_pairing_from_an_in_memory_token_set(self):
        broken = json.loads(json.dumps(IN_MEMORY))
        for token in broken['color']['tokens']:
            if token['name'] == 'ink':
                token['value']['dark'] = '#7f8896'  # same as ink-subtle: 4.14:1 on surface
        failing = [r for r in check.check(broken) if not r['ok']]
        self.assertIn(('surface', 'ink', 'dark'),
                      {(r['ground'], r['ink'], r['theme']) for r in failing})
        self.assertIn(4.14, {r['ratio'] for r in failing})
        # Nothing else in the set changed, so the light rows still pass.
        self.assertNotIn('light', {r['theme'] for r in failing
                                   if (r['ground'], r['ink']) == ('surface', 'ink')})

    def test_current_token_values_and_the_documented_failures(self):
        rows = {(r['ground'], r['ink'], r['theme']): r['ratio']
               for r in check.check(json.loads((ROOT / 'project/tokens.json').read_text()))}
        # 3.64:1 is the #1 value, recorded here once the on-accent token landed.
        self.assertEqual(rows[('accent', 'on-accent', 'dark')], 5.15)
        self.assertEqual({r['ground'] for r in check.check(IN_MEMORY)
                          if not r['ok'] and (r['ground'], r['ink']) in check.PAIRINGS},
                         {'surface', 'bad-soft'})


class ContrastGapTests(unittest.TestCase):
    """The three gaps the vCenter API Simulator UX report measured, held shut."""

    def rows(self):
        tokens = json.loads((ROOT / 'project/tokens.json').read_text())
        return {(r['ground'], r['ink'], r['over'], r['theme']): r for r in check.check(tokens)}

    def test_dark_links_clear_4_5_on_every_ground(self):
        for ground in ('bg', 'surface', 'surface-sunken'):
            with self.subTest(ground=ground):
                self.assertTrue(self.rows()[(ground, 'link', None, 'dark')]['ok'])

    def test_danger_button_label_clears_4_5_in_both_themes(self):
        for theme in ('light', 'dark'):
            with self.subTest(theme=theme):
                self.assertTrue(self.rows()[('bad', 'on-bad', None, theme)]['ok'])

    def test_bad_ink_holds_on_surface_sunken(self):
        for theme in ('light', 'dark'):
            with self.subTest(theme=theme):
                row = self.rows()[('bad-soft', 'bad-ink', 'surface-sunken', theme)]
                self.assertTrue(row['ok'])

    def test_control_borders_clear_3_to_1_in_both_themes(self):
        for theme in ('light', 'dark'):
            for ground in ('bg', 'surface', 'surface-sunken'):
                with self.subTest(theme=theme, ground=ground):
                    row = next(r for r in self.rows().values()
                               if r['kind'] == 'control border' and r['theme'] == theme
                               and r['ground'] == ground)
                    self.assertEqual(row['minimum'], 3.0)
                    self.assertTrue(row['ok'])

    def test_a_line_coloured_border_would_fail(self):
        # The pre-fix input border: `line` on surface, 1.35:1 light.
        self.assertLess(check.contrast_ratio('#d9dee5', '#ffffff'), 3.0)


class CliTests(unittest.TestCase):
    def test_exit_code_follows_the_minimum(self):
        command = [sys.executable, str(ROOT / 'tools/check-contrast.py')]
        strict = subprocess.run([*command, '--minimum', '1'], capture_output=True, text=True)
        self.assertEqual(strict.returncode, 0)
        self.assertIn('All 42 pairings clear 1.0:1', strict.stdout)
        loose = subprocess.run([*command, '--minimum', '9'], capture_output=True, text=True)
        self.assertEqual(loose.returncode, 1)
        self.assertIn('below 9.0:1', loose.stdout)

    def test_json_mode_is_parseable(self):
        done = subprocess.run([sys.executable, str(ROOT / 'tools/check-contrast.py'), '--json'],
                              capture_output=True, text=True, cwd=os.fspath(ROOT))
        self.assertEqual(done.returncode, 0)
        rows = json.loads(done.stdout)
        self.assertEqual(len(rows), 42)


if __name__ == '__main__':
    unittest.main()

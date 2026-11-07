#!/usr/bin/env python3
"""Assert every documented Lattice pairing clears WCAG 2.x contrast.

Text pairings need 4.5:1 (SC 1.4.3). Form-control borders need 3:1 against
the ground they sit on (SC 1.4.11).

The brand book (`project/README.md`, "Using colour") states which ink sits on
which ground. This checks those pairings against `project/tokens.json` in both
themes and exits non-zero when one falls below the minimum, so the next
regression is caught in the repo rather than by a consumer.

    python3 tools/check-contrast.py [--minimum 4.5] [--json]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MINIMUM = 4.5
CONTROL_MINIMUM = 3.0

# (ground, ink, over) text pairs, in the order the brand book's table lists
# them. `over` is the opaque ground a translucent `ground` is composited on, or
# None for the default (surface). Adding a pairing is a one-line change here;
# nothing else in this file enumerates them.
PAIRINGS: list[tuple[str, str, str | None]] = [
    ('bg', 'ink', None),
    ('bg', 'ink-muted', None),
    ('bg', 'link', None),
    ('surface', 'ink', None),
    ('surface', 'ink-muted', None),
    ('surface', 'ink-subtle', None),
    ('surface', 'link', None),
    ('surface-sunken', 'ink', None),
    ('surface-sunken', 'ink-muted', None),
    ('surface-sunken', 'link', None),
    ('accent', 'on-accent', None),
    ('accent-strong', 'on-accent', None),
    ('accent-soft', 'accent-ink', None),
    ('ok-soft', 'ok-ink', None),
    ('warn-soft', 'warn-ink', None),
    ('bad-soft', 'bad-ink', None),
    ('bad-soft', 'bad-ink', 'surface-sunken'),
    ('bad', 'on-bad', None),
]

# Input, textarea and select outlines: (ground, border). The border is
# ink-subtle, and the ground is wherever a control can sit or be disabled.
CONTROL_BORDER_PAIRINGS: list[tuple[str, str]] = [
    ('bg', 'ink-subtle'),
    ('surface', 'ink-subtle'),
    ('surface-sunken', 'ink-subtle'),
]


def resolve(tokens: dict, theme: str) -> dict[str, str]:
    """Colour token name -> resolved CSS value for one theme, aliases expanded."""
    raw = {t['name']: t['value'] for t in tokens['color']['tokens']}

    def value(name: str, trail: tuple[str, ...] = ()) -> str:
        if name in trail:
            raise ValueError(f"Cyclic token alias: {' -> '.join((*trail, name))}")
        current = raw[name]
        if isinstance(current, dict):
            current = current[theme]
        if current.startswith('{') and current.endswith('}'):
            current = value(current[1:-1], (*trail, name))
        return current

    return {name: value(name) for name in raw}


def parse_color(value: str) -> tuple[tuple[float, float, float], float]:
    """'#rgb'/'#rrggbb'/'rgba(r,g,b,a)' -> 8-bit channel triple and alpha."""
    text = value.strip()
    if text.startswith('#'):
        hexed = text[1:]
        if len(hexed) == 3:
            hexed = ''.join(ch * 2 for ch in hexed)
        if len(hexed) not in (6, 8):
            raise ValueError(f'unsupported colour: {value!r}')
        return tuple(int(hexed[i:i + 2], 16) for i in (0, 2, 4)), (
            int(hexed[6:8], 16) / 255 if len(hexed) == 8 else 1.0)
    match = re.fullmatch(r'rgba\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,'
                         r'\s*([\d.]+)\s*\)', text)
    if match:
        r, g, b, alpha = match.groups()
        return (int(r), int(g), int(b)), float(alpha)
    raise ValueError(f'unsupported colour: {value!r}')


def flatten(rgb: tuple[float, float, float], alpha: float,
            base: tuple[float, float, float]) -> tuple[float, float, float]:
    """Composite a translucent colour over an opaque ground, per CSS."""
    if alpha >= 1.0:
        return rgb
    return tuple(alpha * c + (1 - alpha) * k for c, k in zip(rgb, base))


def luminance(rgb: tuple[float, float, float]) -> float:
    """WCAG 2.x relative luminance from 8-bit sRGB channels."""
    def linear(channel: float) -> float:
        channel /= 255
        return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(value_a: str, value_b: str, base: str = '#ffffff') -> float:
    """WCAG contrast ratio of two colours; alpha is flattened on `base`."""
    rgb_a, alpha_a = parse_color(value_a)
    rgb_b, alpha_b = parse_color(value_b)
    back = parse_color(base)[0]
    lum_a = luminance(flatten(rgb_a, alpha_a, back))
    lum_b = luminance(flatten(rgb_b, alpha_b, back))
    high, low = max(lum_a, lum_b), min(lum_a, lum_b)
    return (high + 0.05) / (low + 0.05)


def check(tokens: dict, minimum: float = MINIMUM) -> list[dict]:
    """One row per pairing per theme: text pairings, control borders."""
    rows: list[dict] = []
    # (ground, ink, over, required, kind)
    specs = [(g, i, o, minimum, 'text') for g, i, o in PAIRINGS]
    # A lowered --minimum lowers the control floor too, never raises it.
    specs += [(g, i, None, min(CONTROL_MINIMUM, minimum), 'control border')
              for g, i in CONTROL_BORDER_PAIRINGS]
    for theme in (t['id'] for t in tokens['color']['themes']):
        values = resolve(tokens, theme)
        for ground, ink, over, required, kind in specs:
            # The translucent `-soft` fills sit on the card ground behind them.
            base = values[over or 'surface'] if (over or 'surface') in values else '#ffffff'
            ratio = contrast_ratio(values[ink], values[ground], base)
            # Compare the unrounded ratio; round only for display.
            rows.append({
                'theme': theme,
                'ground': ground,
                'ink': ink,
                'over': over,
                'kind': kind,
                'ratio': round(ratio, 2),
                'minimum': required,
                'ok': ratio >= required,
            })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--minimum', type=float, default=MINIMUM,
                        help=f'required contrast ratio (default {MINIMUM})')
    parser.add_argument('--json', action='store_true', help='emit rows as JSON')
    args = parser.parse_args()

    tokens = json.loads((ROOT / 'project' / 'tokens.json').read_text(encoding='utf-8'))
    rows = check(tokens, args.minimum)

    def label(r: dict) -> str:
        ground = r['ground'] + (f" on {r['over']}" if r['over'] else '')
        return f"{ground} / {r['ink']}" + (' (border)' if r['kind'] == 'control border' else '')

    width = max(len(label(r)) for r in rows)
    failures = [r for r in rows if not r['ok']]

    if args.json:
        # One JSON document on stdout; the human-readable table goes to stderr.
        sys.stdout.write(json.dumps(rows, indent=2) + '\n')
        def report(line: str) -> None:
            print(line, file=sys.stderr)
    else:
        report = print

    report(f"{'theme':6}  {'pairing':<{width}}  {'ratio':>6}  status")
    for row in rows:
        report(f"{row['theme']:6}  {label(row):<{width}}"
               f"  {row['ratio']:>6.2f}  {'ok' if row['ok'] else 'FAIL'}")
    if failures:
        report(f"\n{len(failures)} pairing(s) below {args.minimum}:1 (text) / "
               f"{min(CONTROL_MINIMUM, args.minimum)}:1 (control borders)")
        for row in failures:
            report(f"  {row['theme']}: {label(row)}"
                   f" = {row['ratio']:.2f}:1 (needs {row['minimum']}:1)")
        raise SystemExit(1)
    report(f"\nAll {len(rows)} pairings clear {args.minimum}:1"
           f" (text) / {min(CONTROL_MINIMUM, args.minimum)}:1 (control borders)")


if __name__ == '__main__':
    main()

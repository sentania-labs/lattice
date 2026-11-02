#!/usr/bin/env python3
"""Assert every documented Lattice text pairing clears WCAG 2.x 4.5:1.

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

# (ground, ink) pairs, in the order the brand book's table lists them.
# Adding a pairing is a one-line change here; nothing else in this file
# enumerates them.
PAIRINGS: list[tuple[str, str]] = [
    ('bg', 'ink'),
    ('bg', 'ink-muted'),
    ('surface', 'ink'),
    ('surface', 'ink-muted'),
    ('surface', 'ink-subtle'),
    ('surface-sunken', 'ink'),
    ('surface-sunken', 'ink-muted'),
    ('accent', 'on-accent'),
    ('accent-strong', 'on-accent'),
    ('accent-soft', 'accent-ink'),
    ('ok-soft', 'ok-ink'),
    ('warn-soft', 'warn-ink'),
    ('bad-soft', 'bad-ink'),
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
    """One row per documented pairing per theme, in table order."""
    rows: list[dict] = []
    for theme in (t['id'] for t in tokens['color']['themes']):
        values = resolve(tokens, theme)
        # The translucent `-soft` fills sit on the card ground behind them.
        base = values['surface'] if 'surface' in values else '#ffffff'
        for ground, ink in PAIRINGS:
            ratio = contrast_ratio(values[ink], values[ground], base)
            # Compare the unrounded ratio; round only for display.
            rows.append({
                'theme': theme,
                'ground': ground,
                'ink': ink,
                'ratio': round(ratio, 2),
                'minimum': minimum,
                'ok': ratio >= minimum,
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

    width = max(len(f"{r['ground']} / {r['ink']}") for r in rows)
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
        report(f"{row['theme']:6}  {row['ground'] + ' / ' + row['ink']:<{width}}"
               f"  {row['ratio']:>6.2f}  {'ok' if row['ok'] else 'FAIL'}")
    if failures:
        report(f"\n{len(failures)} pairing(s) below {args.minimum}:1")
        for row in failures:
            report(f"  {row['theme']}: {row['ground']} / {row['ink']}"
                   f" = {row['ratio']:.2f}:1")
        raise SystemExit(1)
    report(f"\nAll {len(rows)} pairings clear {args.minimum}:1")


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Build preview.html: every component on one page, from the compiled dist files.

This is the local review surface. It reads what a consuming app would actually
vendor (dist/tokens.css and dist/lattice.css), so if it looks right here, an app
linking those two files gets the same result. Open the file directly in a
browser; it needs no server.
"""
from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
ORDER = ["Cover", "Button", "Form", "Tabs", "Card", "Alert", "Badge", "Table", "Tree"]

sections = []
for name in ORDER:
    path = ROOT / "project" / "components" / name / "preview.html"
    if not path.exists():
        continue
    html = re.sub(r"^<!--.*?-->\s*", "", path.read_text(encoding="utf-8"), flags=re.S)
    sections.append(f'<section><h2 class="lat-preview-h">{name}</h2>{html}</section>')

page = f"""<!doctype html>
<html lang="en" data-theme="light">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Lattice</title>
<style>{(ROOT / "dist" / "tokens.css").read_text(encoding="utf-8")}</style>
<style>{(ROOT / "dist" / "lattice.css").read_text(encoding="utf-8")}</style>
<style>
  body {{ padding: 0 0 40px; }}
  .lat-preview-bar {{
    position: sticky; top: 0; z-index: 10; display: flex; align-items: center;
    gap: 12px; padding: 10px 18px; background: var(--surface);
    border-bottom: 1px solid var(--line);
  }}
  .lat-preview-bar h1 {{
    margin: 0; font-size: 17px; font-weight: 650; letter-spacing: -0.01em;
  }}
  .lat-preview-bar .lat-ver {{ margin-right: auto; }}
  .lat-preview-h {{
    margin: 24px 18px 4px; font-size: 11px; font-weight: 650;
    text-transform: uppercase; letter-spacing: .08em; color: var(--ink-subtle);
  }}
  section {{ border-top: 1px solid var(--line); }}
  section:first-of-type {{ border-top: 0; }}
</style>
</head>
<body>
<div class="lat-preview-bar">
  <h1>Lattice</h1>
  <span class="lat-ver">local preview</span>
  <button class="lat-btn" id="lat-theme">Dark</button>
</div>
{"".join(sections)}
<script>
  var root = document.documentElement, btn = document.getElementById('lat-theme');
  btn.addEventListener('click', function () {{
    var dark = root.getAttribute('data-theme') === 'dark';
    root.setAttribute('data-theme', dark ? 'light' : 'dark');
    btn.textContent = dark ? 'Dark' : 'Light';
  }});
</script>
</body>
</html>
"""

(ROOT / "preview.html").write_text(page, encoding="utf-8")
print(f"wrote preview.html ({len(sections)} components)")

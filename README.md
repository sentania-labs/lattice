# Lattice

The shared look for the VCF helper tools: vcf-cf-migrator, vcf-lab-services,
vcf-doctor, and what comes after them.

Lattice is a stylesheet and a set of design tokens. There is no npm package, no
build step for consumers, and no runtime. An app links two static CSS files and
writes ordinary HTML, which is what lets it work in a Flask template, in a
Python-rendered page inside a signed offline executable, and in a React app
alike.

It was extracted from `sentania-labs/vcf-cf-migrator`, which already carried two
coherent stylesheets: `uipage.py` (the tool's light chrome) became the light
theme, and `preview.py` (the dark VCF Operations dashboard skin) became the dark
theme. Every colour here is a value one of those files already used.

## Consuming it

Copy `dist/tokens.css` and `dist/lattice.css` into the app and link them in that
order:

```html
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="lattice.css">
```

Dark theme is an attribute on the root element. Light is the default:

```html
<html data-theme="dark">
```

## Layout of this repo

| Path | What |
| --- | --- |
| `project/tokens.json` | The tokens. The source of truth for every colour, type style, spacing step and radius. |
| `project/README.md` | The brand book: principles, contrast pairings, usage rules. |
| `project/components/bundle.css` | The component layer, authored here. |
| `project/components/<Name>/` | Per-component guidelines and a live preview. |
| `dist/tokens.css` | Generated from `tokens.json`. Do not edit. |
| `dist/lattice.css` | A copy of the component layer under its consuming name. |
| `tools/build-tokens.py` | Compiles `tokens.json` into `dist/tokens.css`. |

After editing `project/tokens.json`:

```bash
python3 tools/build-tokens.py
cp project/components/bundle.css dist/lattice.css
```

## The design system page

The same `project/` tree is published as a browsable design system with live
component previews, which is the surface to review changes on rather than
reading CSS diffs.

That page is convenience, not the source of truth. This repo is. The page can be
rebuilt from these files at any time, on any account, with a single publish, so
nothing here depends on it continuing to exist.

## Principles, in short

- Borders, not shadows. There is no elevation scale.
- One accent, spent only on the primary action, links, selection and focus.
- `ok`, `warn` and `bad` carry state and nothing else.
- Density is the point. These are administrator tools.
- Every token has a light and a dark value.

The full versions, with the contrast pairings that are not negotiable, are in
`project/README.md`.

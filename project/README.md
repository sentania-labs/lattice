# Lattice

Lattice is the shared look for Scott Bowe's VCF helper tools: vcf-cf-migrator,
vcf-lab-services, vcf-doctor, and whatever comes after them. It is a stylesheet
and a set of tokens, not a framework. There is no npm package, no build step and
no runtime. You link two CSS files and write ordinary HTML.

It exists so those tools look like they came from the same place, and look at
home beside the VCF consoles an administrator already has open, without taking a
dependency on anyone else's design system.

## Where it came from

Lattice was not designed from nothing. It was extracted from
`sentania-labs/vcf-cf-migrator`, which already carried two coherent stylesheets:

- `src/vcfcf_migrator/uipage.py`, the tool's own light chrome, became the light theme.
- `src/vcfcf_migrator/preview.py`, the dark skin used to render a VCF Operations
  dashboard preview, became the dark theme.

Every colour in this system is a value one of those two files already used. That
is why the first release looks like work you have already shipped rather than a
new opinion.

## Principles

**Borders, not shadows.** There is no elevation scale and no shadow token.
Separation comes from `line` and `line-soft` against `surface` and
`surface-sunken`. A tool that shows a thousand rows cannot afford soft edges,
and the moment shadows appear the screen starts to feel like a consumer app.

**One accent, spent carefully.** `accent` is the only chromatic colour in the
interface that does not mean a state. It marks the primary action, the active
tab, links, selection and focus. If two things on a screen are competing in
`accent`, one of them is not the primary action.

**Colour is reserved for meaning.** `ok`, `warn` and `bad` carry state and
nothing else. Never reach for them to add visual interest, and never use a
state colour as a brand colour.

**Density is the point.** These are administrator tools. Default to `ui` (13px)
for controls and `body` (14px) for reading, not larger. Padding comes from the
lower half of the spacing scale. Whitespace is earned by grouping, not by
inflating every element.

**Both themes, always.** Every token carries a light and a dark value. Dark is
not an afterthought here: it is where the dashboard previews live, and it is what
an administrator staring at a VCF console all day is already in.

## Using colour

| Ground | Text on it |
| --- | --- |
| `bg` | `ink`, `ink-muted` |
| `surface` | `ink`, `ink-muted`, `ink-subtle` for metadata |
| `surface-sunken` | `ink`, `ink-muted` |
| `accent-soft` | `accent-ink` |
| `ok-soft` | `ok-ink` |
| `warn-soft` | `warn-ink` |
| `bad-soft` | `bad-ink` |

Two rules that are not negotiable:

1. **Never put `ink-subtle` on `surface-sunken` for anything a person has to
   read.** It is a metadata colour on a plain surface, and it gives up contrast
   the moment the ground darkens.
2. **A state colour never appears without its `-soft` ground or its `-ink`
   partner.** `bad` on `surface` as body text is a contrast failure waiting for a
   theme change; `bad-ink` on `bad-soft` is not.

`focus` is an alias of `accent` on purpose. A focus ring that changes colour with
the state of the thing it is on stops reading as focus.

## Type

Two families, both system stacks: `sans` for everything, `mono` for code,
identifiers and any number a person will compare against another number.

The scale runs 10.5px to 17px. That is narrow, deliberately. A tool with one
17px title, 14px body and 13px controls reads as one screen; a tool with a
display scale reads as a marketing page. `section-label` and `micro` are meant to
be set in uppercase, which is what does the work at those sizes.

Use `mono` wherever alignment carries meaning: object keys, shas, versions, and
any table column of figures.

## Iconography

Lattice ships no icon set. The migrator draws its disclosure arrows from text
glyphs, and that remains the recommendation: for a handful of affordances, a
character costs nothing and never fails to load. If a tool needs a real icon set,
add it there and keep it out of Lattice until a second tool needs the same one.

## Spacing and shape

`space-7` (16px) is the default: card padding, and the gap between cards.
Reach below it for anything inside a component, above it only to separate
regions of a screen.

Radii step down as surfaces nest: `radius-xl` on a card, `radius-lg` on a button
or input inside it, `radius-md` on a widget or tile, `radius-sm` on a badge.
Nesting two elements at the same radius is what makes a panel look like a sticker.

## Consuming it

Two files, in this order:

```html
<link rel="stylesheet" href="tokens.css">
<link rel="stylesheet" href="lattice.css">
```

`tokens.css` declares the custom properties and the type-style classes.
`lattice.css` is the component layer (this system's `components/bundle.css`).
Both are static files with no dependencies, which is what lets the migrator
vendor them into a signed offline executable and lets a Flask app serve them
from `static/`.

Switch themes by setting the attribute on the root element:

```html
<html data-theme="dark">
```

Light is the default and needs no attribute.

## Not synced

- **Fonts:** none fetched. Lattice uses system font stacks by design, so
  `type.fonts` is empty and there is nothing to vendor.
- **Components:** not built from code. The migrator renders HTML from Python
  string templates rather than exporting a component library, so there was no
  bundle to build. The component layer here is hand-written CSS derived from
  those templates, and each component's guidelines name the source it came from.
  Previews are plain markup styled by that CSS, which is exactly how a consuming
  app uses it.
- **Not carried over:** the migrator's outer dark frame (`#11151a`, the body
  behind a dashboard preview) has no light counterpart in the source, so it is
  not a token. If a tool needs a deeper ground behind `bg`, that is a request to
  add one properly, in both themes.

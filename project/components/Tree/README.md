A collapsible tree of rows, for content and the dependencies it drags along.

`.lat-group` is a collapsible section with a count pushed to the right in
`ink-subtle`. The disclosure arrow is a text glyph on `::before`, which is why
Lattice ships no icon set: for one affordance a character never fails to load.

Each row is `.lat-row`, a flex line that wraps. `.is-sel` tints the row
`accent-soft` to mark selection; hover uses `surface-sunken`. Nested `<ul>`
levels indent by `space-7` and carry a `line-soft` guide on the left edge, so
depth is readable without any row-level decoration.

`.lat-why` is the explanation line, and it takes `flex-basis: 100%` so it
always falls onto its own line beneath the name. That is deliberate and it was
measured: letting the reason share a line with the name squeezed both, and on a
real export at 1280px more than half the rows grew past 60px tall with names
crushed into a narrow column. Keep the reason on its own line.

The consumer supplies the interaction. These are classes over a real `<ul>`,
and the migrator drives them with `<details>` so the tree works with no
JavaScript at all.

Derived from `uipage.py`, the `.kindgroup`, `ul.tree`, `.row` and `.why` rules.

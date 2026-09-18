The page's primary container: a bordered surface with an uppercase section label.

`.lat-card` is `surface` inside one `line` border at `radius-xl`, with
`space-7` padding. It is the outermost box on a page, so nothing nests a card
inside a card. When content needs grouping inside one, use `surface-sunken` and
a smaller radius instead.

The heading is `.lat-card-title` (or a plain `h2` inside the card): 13px,
uppercase, `0.06em` tracking, in `ink-subtle`. Set small and quiet on purpose,
so a screen with eight cards reads as content with labels rather than eight
competing headlines.

`.lat-code` is the recessed block for JSON, paths and command output. It uses
`surface-sunken` and the mono family, and scrolls horizontally rather than
wrapping, because a wrapped identifier is harder to read than a scrolled one.

The consumer supplies the grid. Lattice does not ship a layout system; cards
sit in whatever CSS grid the page defines. Give grid children `min-width: 0`
or a long line inside `.lat-code` will stretch the whole page.

Derived from `uipage.py`, the `.card`, `h2` and `pre` rules.

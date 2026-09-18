Two small markers with different jobs: pills count things, badges classify them.

`.lat-pill` is a rounded count. The label sits in `ink-muted` and the figure in
`<b>` switches to `ink` with tabular numerals, so a row of pills stays aligned
as the numbers change. Add `.is-on` to mark the one the person is filtering by,
which tints it `accent-soft`.

`.lat-badge` is a squared-off classifier at `radius-sm`, set uppercase at
10.5px. Use it for the kind of a thing or the state of a thing, never for a
count. The state modifiers follow the same `-soft` ground and `-ink` text rule
as banners.

Keep both short. A badge holding a sentence is a banner.

Derived from `uipage.py`'s `.pill` rules and `preview.py`'s `.pv-flow` and
widget type tags.

The sticky application header and the single row of tabs beneath it.

`.lat-header` holds the tool's name, its version in mono `ink-subtle`, and any
control that belongs to the whole screen rather than to one tab. It sticks to
the top and carries one `line` rule beneath it. There is one per application.

`.lat-tabs` is the only navigation pattern in Lattice. The active tab is marked
by a 2px `accent` underline and a weight change, never by a filled background:
a filled tab reads as a button and invites a second click. Tabs are real
`<button>` elements inside a form, so they work without JavaScript, which is
what lets the migrator render them server side.

Do not nest a second row of tabs inside a tab. If a tab needs its own sections,
that is a card per section.

Derived from `uipage.py`, the `header.top` and `nav.tabs` rules.

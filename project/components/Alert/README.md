A full-width message whose state is carried by a 3px left rule and a tinted ground.

Four states plus a neutral default. `--ok` confirms something finished,
`--warn` flags something the person should look at before continuing, `--bad`
reports a failure, and `--info` explains the screen rather than reacting to an
action. A `.lat-banner` with no modifier is neutral and is the right choice for
an empty state.

Each variant pairs its `-soft` ground with its `-ink` text, never the raw state
colour as text. That pairing is what holds contrast when the theme flips.

Text wraps with `white-space: pre-wrap`, so a multi-line message from a tool's
own output keeps its line breaks instead of collapsing into a paragraph.

The consumer supplies placement. A banner about the whole screen goes directly
under the header; a banner about one card goes inside that card.

Derived from `uipage.py`, the `.msg` and `.err` rules, and from `preview.py`'s
banner and "nothing to show" panels.

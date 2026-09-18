Text inputs and textareas, with the label above and the hint below.

Every control gets a real `<label class="lat-label">` immediately above it, at
12px in `ink-muted`. Placeholder text is not a label and never replaces one:
it disappears exactly when the person needs it.

`.lat-hint` carries supporting detail under the control in `ink-subtle`. Add
`.lat-hint--bad` when it is reporting a problem with what was entered, which
switches it to `bad-ink` rather than to `bad`, so the message stays readable in
both themes.

`.lat-textarea` sets the mono family, because a textarea in these tools almost
always holds keys, paths or raw content where alignment matters.

The consumer supplies validation. Lattice styles the states; it does not decide
when a field is wrong.

Derived from `uipage.py`, the `input[type=text]`, `textarea` and `label` rules.

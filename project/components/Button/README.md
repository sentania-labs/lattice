The action control, in four weights, with exactly one primary per view.

Use `.lat-btn` for every button and add a modifier only when the button earns
it. `.lat-btn--primary` is the single action the screen exists to perform, and
a screen showing two primaries has not decided what it is for.
`.lat-btn--ghost` is for actions that sit inside a row or a header and should
not compete with the content: clearing a field, expanding a group.
`.lat-btn--danger` is for a destructive action only, never for emphasis.

The consumer supplies the element. These are classes on a real `<button>`, not
a component, so keyboard behaviour, `disabled` and form submission are the
browser's. Do not put them on an `<a>` unless it genuinely navigates.

Colour comes from `accent` and `accent-strong` on hover. Borders are `line`,
which is what keeps a row of default buttons quiet next to one primary.

Derived from `uipage.py`, the `button`, `button.primary` and `button.ghost`
rules.

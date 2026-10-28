# Lattice

The shared look for the VCF helper tools: vcf-cf-migrator, vcf-lab-services,
vcf-doctor, and what comes after them.

Lattice ships web CSS and Qt Style Sheets from the same design tokens. There
is no npm package, build step for consumers, or Lattice runtime. Web apps link
two static CSS files; Qt Widgets apps load a QSS file and matching palette,
in any language that uses Qt.

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

## Qt Widgets

Vendor `dist/lattice.qss` (light) or `dist/lattice-dark.qss` (dark), plus
`dist/lattice-palette.json`. QSS contains resolved values and needs no assets or
Python runtime. This covers Qt Widgets in PySide6, PyQt, C++, and other Qt
bindings. Qt Quick/QML and other native toolkits need separate integrations.

Use the Fusion widget style for consistent rendering. Set QPalette **before**
QSS: native arrows, check/radio indicators, placeholder text, disabled text,
viewports, and controls outside the styled set also consume palette roles.
`Window` maps to `bg`, `Base`/`Button` to `surface`, `AlternateBase` to
`surface-sunken`, text to `ink`, and `Highlight`/`HighlightedText` to
`accent`/`on-accent`. The generated JSON includes Active, Inactive, and Disabled
groups; apply all three. Native OS dialogs and title bars may retain OS colors.
Reapply both palette and QSS when switching themes.

PySide6, after constructing `QApplication`:

```python
import json
from pathlib import Path
from PySide6.QtGui import QColor, QPalette

assets = Path("path/to/vendored/lattice")
theme = "dark"  # or "light"
app.setStyle("Fusion")
palette = QPalette()
for group, roles in json.loads((assets / "lattice-palette.json").read_text())[theme].items():
    for name, color in roles.items():
        role = getattr(QPalette.ColorRole, name, None)
        if role is not None:  # Accent was added in Qt 6.6.
            palette.setColor(getattr(QPalette.ColorGroup, group), role, QColor(color))
app.setPalette(palette)
filename = "lattice.qss" if theme == "light" else "lattice-dark.qss"
app.setStyleSheet((assets / filename).read_text())
button.setProperty("variant", "primary")
card.setProperty("lattice", "card")  # QFrame
```

C++ (Qt 6), after constructing `QApplication app(argc, argv)`:

```cpp
#include <QApplication>
#include <QColor>
#include <QFile>
#include <QHash>
#include <QJsonDocument>
#include <QJsonObject>
#include <QPalette>
#include <stdexcept>

// Inside your setup function:
const QString assets = "path/to/vendored/lattice/";
const QString theme = "dark";  // or "light"
auto read = [&](const QString &name) {
    QFile file(assets + name);
    if (!file.open(QIODevice::ReadOnly))
        throw std::runtime_error("Cannot open Lattice asset");
    return file.readAll();
};
app.setStyle("Fusion");
const auto colors = QJsonDocument::fromJson(read("lattice-palette.json"))
                        .object().value(theme).toObject();
const QHash<QString, QPalette::ColorRole> roles = {
    {"Window", QPalette::Window}, {"WindowText", QPalette::WindowText},
    {"Base", QPalette::Base}, {"AlternateBase", QPalette::AlternateBase},
    {"Text", QPalette::Text}, {"Button", QPalette::Button},
    {"ButtonText", QPalette::ButtonText}, {"BrightText", QPalette::BrightText},
    {"Highlight", QPalette::Highlight}, {"HighlightedText", QPalette::HighlightedText},
    {"ToolTipBase", QPalette::ToolTipBase}, {"ToolTipText", QPalette::ToolTipText},
    {"Link", QPalette::Link}, {"LinkVisited", QPalette::LinkVisited},
    {"PlaceholderText", QPalette::PlaceholderText}, {"Light", QPalette::Light},
    {"Midlight", QPalette::Midlight}, {"Mid", QPalette::Mid},
    {"Dark", QPalette::Dark}, {"Shadow", QPalette::Shadow},
#if QT_VERSION >= QT_VERSION_CHECK(6, 6, 0)
    {"Accent", QPalette::Accent},
#endif
};
const QHash<QString, QPalette::ColorGroup> groups = {
    {"Active", QPalette::Active}, {"Inactive", QPalette::Inactive},
    {"Disabled", QPalette::Disabled},
};
QPalette palette;
for (auto g = groups.cbegin(); g != groups.cend(); ++g) {
    const auto values = colors.value(g.key()).toObject();
    for (auto r = roles.cbegin(); r != roles.cend(); ++r)
        palette.setColor(g.value(), r.value(), QColor(values.value(r.key()).toString()));
}
app.setPalette(palette);
app.setStyleSheet(QString::fromUtf8(read(theme == "light" ? "lattice.qss" : "lattice-dark.qss")));
button->setProperty("variant", "primary");
card->setProperty("lattice", "card");  // QFrame
```

### Component mapping

Set properties before showing widgets. If a property changes later, call
`widget.style().unpolish(widget)` then `widget.style().polish(widget)` and
`widget.update()` (C++: `widget->style()->unpolish(widget)`, etc.). Properties
are strings. The stylesheet styles standard controls automatically; only variants
and semantic containers require properties.

| Lattice component | Qt widget / property |
| --- | --- |
| Button | `QPushButton`, `QToolButton`; `variant="primary"`, `"ghost"`, or `"danger"`; no property for default. Hover, pressed, checked, focus, disabled supported. Danger uses `bad-soft`/`bad-ink` with a `bad` border. |
| Card | `QFrame`, `lattice="card"`. Set layout contents margins to 16px and spacing to 8px; QSS does not set layout gaps. |
| Form | `QLineEdit`, `QTextEdit`, `QPlainTextEdit`, `QComboBox`, spin/date/time boxes; `QCheckBox` and `QRadioButton` retain native indicators, including partial checks. |
| Form labels / hints | `QLabel`, `lattice="label"` or `"hint"`; hints accept `status="bad"`. |
| Tabs | `QTabWidget` / `QTabBar`; Qt owns selection and keyboard behavior. |
| Alert | `QLabel`, `lattice="banner"`, `status="ok"`, `"warn"`, `"bad"`, or `"info"`. Set word wrap in code for multiline text. |
| Badge | `QLabel`, `lattice="badge"`, same status values. |
| Pill | `QLabel`, `lattice="pill"`; `status="info"` for active. Rounded rectangle rather than CSS's automatic pill radius. |
| Table / Tree | `QTableView` / `QTableWidget`, `QTreeView` / `QTreeWidget`; standard headers and selection. Enable alternating row colors in code; Qt models/delegates own cell formatting. |
| Navigation list | `QListWidget`, `lattice="steps"`. |
| Header / sidebar | `QFrame`, `lattice="header"` / `"sidebar"`; set layout margins in code. |
| Typography | `QLabel`, `lattice` equal to a token type style, e.g. `"page-title"`, `"section-label"`, `"subhead"`, `"caption"`, `"code"`; `"muted"` for secondary text. Supply uppercase label text in code. |
| Code | `QPlainTextEdit` / `QTextEdit`, `lattice="code"`; set read-only in code as needed. |
| Cover | No widget equivalent; compose a window with title, supporting text and cards. |

Use `objectName="lattice-root"` on a plain root `QWidget` for page background;
`QMainWindow` and `QDialog` receive it automatically. Progress bars, group boxes,
menus, toolbars, status bars, and horizontal/vertical scrollbars are also styled.
The platform UI font stays native; code styles use the token stack’s terminal
`monospace` generic because Qt does not resolve CSS font fallback lists.
QSS cannot implement CSS layout, line height, shadows, or HTML typography rules.
Custom painted widgets and delegates must use the palette or tokens themselves.
Coverage builds on [the Telegraf helper's Qt translation](https://github.com/sentania-labs/vcf-ops-telegraf-helper/blob/main/vcf_ops_telegraf_helper/gui/theme.py),
with current token values, both themes, and no external arrow assets.

### Build and inspect

```bash
python3 tools/build-qt.py
python3 tools/build-qt.py --check
python3 -m unittest discover -s tools/tests
# Optional visual dependency: install PySide6 into your development environment.
QT_QPA_PLATFORM=offscreen python3 tools/preview-qt.py --output /tmp/lattice-qt
```

The preview writes `lattice-light.png` and `lattice-dark.png` for visual review
and rejects QSS parser warnings. No existing CSS freshness check or CI workflow
exists in this repository; `build-qt.py --check` provides that check for all Qt
artifacts and can be run by a caller's validation pipeline.

## Layout of this repo

| Path | What |
| --- | --- |
| `project/tokens.json` | The tokens. The source of truth for every colour, type style, spacing step and radius. |
| `project/README.md` | The brand book: principles, contrast pairings, usage rules. |
| `project/components/bundle.css` | The component layer, authored here. |
| `project/components/<Name>/` | Per-component guidelines and a live preview. |
| `dist/tokens.css` | Generated from `tokens.json`. Do not edit. |
| `dist/lattice.css` | A copy of the component layer under its consuming name. |
| `dist/lattice.qss`, `dist/lattice-dark.qss` | Generated light (default) and dark Qt Widgets themes. |
| `dist/lattice-palette.json` | Generated QPalette colors for both themes and all color groups. |
| `tools/build-qt.py` | Generates Qt artifacts; `--check` detects stale output without writing. |
| `tools/preview-qt.py` | PySide6 offscreen component gallery for visual review. |
| `tools/build-tokens.py` | Compiles `tokens.json` into `dist/tokens.css`. |

After editing `project/tokens.json`:

```bash
python3 tools/build-tokens.py
python3 tools/build-qt.py
python3 tools/build-qt.py --check
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

"""Render disabled text through Qt's real stylesheet consumer (optional PySide6)."""
import importlib.util
import os
from pathlib import Path
import unittest

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
try:
    from PySide6.QtGui import QColor, QPainter, QPalette, QPixmap
    from PySide6.QtWidgets import (
        QApplication, QGroupBox, QLabel, QListWidget, QMenu, QMenuBar,
        QProgressBar, QStatusBar, QStyle, QStyleOptionMenuItem, QToolBar, QWidget,
    )
except ImportError:
    QApplication = None

ROOT = Path(__file__).resolve().parents[2]


@unittest.skipIf(QApplication is None, 'PySide6 is needed for live Qt rendering')
class DisabledTextTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        spec = importlib.util.spec_from_file_location('build_qt_disabled', ROOT / 'tools/build-qt.py')
        cls.build = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.build)
        import json
        cls.tokens = json.loads((ROOT / 'project/tokens.json').read_text())

    def apply_theme(self, theme):
        self.app.setStyle('Fusion')
        colors = self.build.resolve_tokens(self.tokens, theme)
        palette = QPalette()
        for group, roles in self.build.palette(colors).items():
            for name, value in roles.items():
                role = getattr(QPalette.ColorRole, name, None)
                if role is not None:
                    palette.setColor(getattr(QPalette.ColorGroup, group), role, QColor(value))
        self.app.setPalette(palette)
        self.app.setStyleSheet(self.build.stylesheet(self.tokens, theme))
        return colors

    def test_disabled_actions_render_disabled_ink(self):
        for theme in ('light', 'dark'):
            colors = self.apply_theme(theme)
            for widget_type, element in ((QMenu, QStyle.ControlElement.CE_MenuItem),
                                         (QMenuBar, QStyle.ControlElement.CE_MenuBarItem)):
                for enabled in (True, False):
                    with self.subTest(theme=theme, widget=widget_type.__name__, enabled=enabled):
                        widget = widget_type()
                        action = widget.addAction('MMMM disabled command')
                        action.setEnabled(enabled)
                        widget.ensurePolished()
                        widget.adjustSize()
                        option = QStyleOptionMenuItem()
                        widget.initStyleOption(option, action)
                        option.rect = widget.actionGeometry(action)
                        pixmap = QPixmap(widget.size())
                        pixmap.fill(QColor(colors['surface']))
                        painter = QPainter(pixmap)
                        widget.style().drawControl(element, option, painter, widget)
                        painter.end()
                        image = pixmap.toImage()
                        pixels = {image.pixelColor(x, y).name()
                                  for x in range(image.width()) for y in range(image.height())}
                        expected = colors['ink'] if enabled else colors['ink-subtle']
                        self.assertIn(expected, pixels)
                        if not enabled:
                            self.assertNotIn(colors['ink'], pixels)
                        widget.close()

    def test_disabled_selected_items_use_disabled_selection_colors(self):
        for theme in ('light', 'dark'):
            colors = self.apply_theme(theme)
            for component in ('', 'steps'):
                with self.subTest(theme=theme, component=component):
                    widget = QListWidget()
                    if component:
                        widget.setProperty('lattice', component)
                    widget.addItem('MMMM unavailable')
                    widget.setCurrentRow(0)
                    widget.setEnabled(False)
                    widget.resize(260, 100)
                    widget.show()
                    self.app.processEvents()
                    image = widget.viewport().grab().toImage()
                    rect = widget.visualItemRect(widget.item(0))
                    self.assertEqual(image.pixelColor(rect.right() - 10, rect.center().y()),
                                     QColor(colors['surface-sunken']))
                    self.assertEqual(widget.palette().color(QPalette.ColorGroup.Disabled,
                                                            QPalette.ColorRole.HighlightedText),
                                     QColor(colors['ink-subtle']))
                    widget.close()

    def test_disabled_widgets_do_not_keep_enabled_foreground(self):
        for theme in ('light', 'dark'):
            colors = self.apply_theme(theme)
            cases = [QWidget(), QLabel('Label'), QGroupBox('Group'), QProgressBar(),
                     QListWidget(), QStatusBar(), QToolBar()]
            for component in ('section-label', 'label', 'hint', 'muted', 'banner', 'badge', 'pill'):
                widget = QLabel('Label')
                widget.setProperty('lattice', component)
                widget.setProperty('status', 'bad')
                cases.append(widget)
            for widget in cases:
                with self.subTest(theme=theme, widget=type(widget).__name__, component=widget.property('lattice')):
                    widget.setEnabled(False)
                    widget.ensurePolished()
                    actual = widget.palette().color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText)
                    self.assertEqual(actual, QColor(colors['ink-subtle']))
                    widget.close()


if __name__ == '__main__':
    unittest.main()

#!/usr/bin/env python3
"""Render a representative Qt window. Requires PySide6, not needed by consumers.

QT_QPA_PLATFORM=offscreen python3 tools/preview-qt.py --output /tmp/lattice-qt
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from PySide6.QtCore import Qt, qInstallMessageHandler
from PySide6.QtGui import QColor, QFontInfo, QPalette
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFrame, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QMainWindow, QPlainTextEdit, QProgressBar, QPushButton,
    QRadioButton, QSpinBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)

ROOT = Path(__file__).resolve().parent.parent


def apply_theme(app: QApplication, theme: str) -> None:
    app.setStyle('Fusion')
    roles = json.loads((ROOT / 'dist/lattice-palette.json').read_text())[theme]
    palette = QPalette()
    for group, colors in roles.items():
        for role, color in colors.items():
            color_role = getattr(QPalette.ColorRole, role, None)
            if color_role is not None:
                palette.setColor(getattr(QPalette.ColorGroup, group), color_role, QColor(color))
    app.setPalette(palette)
    name = 'lattice.qss' if theme == 'light' else 'lattice-dark.qss'
    app.setStyleSheet((ROOT / 'dist' / name).read_text())


def label(text: str, component: str, status: str = '') -> QLabel:
    widget = QLabel(text)
    widget.setProperty('lattice', component)
    if status:
        widget.setProperty('status', status)
    return widget


def sample(theme: str) -> QMainWindow:
    window = QMainWindow()
    window.setWindowTitle(f'Lattice / Qt / {theme}')
    root = QWidget()
    root.setObjectName('lattice-root')
    window.setCentralWidget(root)
    layout = QVBoxLayout(root)
    layout.setContentsMargins(18, 18, 18, 18)
    layout.setSpacing(12)
    layout.addWidget(label(f'Lattice / Qt / {theme.title()}', 'page-title'))
    layout.addWidget(label('Shared tokens. Any Qt language. Dense tools, clear state.', 'muted'))
    card = QFrame()
    card.setProperty('lattice', 'card')
    grid = QGridLayout(card)
    grid.setContentsMargins(16, 16, 16, 16)
    grid.setSpacing(12)
    grid.addWidget(label('CONNECTION', 'section-label'), 0, 0, 1, 2)
    grid.addWidget(label('Server address', 'label'), 1, 0)
    grid.addWidget(label('Environment', 'label'), 1, 1)
    address = QLineEdit('vcf.lab.example')
    address.setObjectName('server')
    grid.addWidget(address, 2, 0)
    combo = QComboBox()
    combo.addItems(['Production', 'Staging', 'Development'])
    grid.addWidget(combo, 2, 1)
    grid.addWidget(label('Use a fully qualified hostname.', 'hint'), 3, 0)
    grid.addWidget(QLineEdit(placeholderText='Optional description'), 4, 0)
    disabled = QLineEdit('Managed by policy')
    disabled.setEnabled(False)
    grid.addWidget(disabled, 4, 1)
    options = QHBoxLayout()
    check = QCheckBox('Verify TLS')
    check.setChecked(True)
    options.addWidget(check)
    partial = QCheckBox('Partial selection')
    partial.setCheckState(Qt.CheckState.PartiallyChecked)
    options.addWidget(partial)
    radio = QRadioButton('Live')
    radio.setChecked(True)
    options.addWidget(radio)
    spin = QSpinBox()
    spin.setValue(3)
    options.addWidget(spin)
    grid.addLayout(options, 5, 0, 1, 2)
    buttons = QHBoxLayout()
    for text, variant in [('Connect', 'primary'), ('Cancel', ''), ('Details', 'ghost'), ('Remove', 'danger'), ('Unavailable', 'primary')]:
        button = QPushButton(text)
        button.setObjectName(text)
        if variant:
            button.setProperty('variant', variant)
        button.setEnabled(text != 'Unavailable')
        buttons.addWidget(button)
    grid.addLayout(buttons, 6, 0, 1, 2)
    layout.addWidget(card)
    tabs = QTabWidget()
    results = QWidget()
    results_layout = QHBoxLayout(results)
    table = QTableWidget(4, 3)
    table.setHorizontalHeaderLabels(['Service', 'State', 'Nodes'])
    for row, values in enumerate([('Operations', 'Healthy', '12'), ('Automation', 'Healthy', '4'), ('Network', 'Review', '8'), ('Logs', 'Offline', '2')]):
        for column, text in enumerate(values):
            table.setItem(row, column, QTableWidgetItem(text))
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    table.selectRow(0)
    table.horizontalHeader().setStretchLastSection(True)
    results_layout.addWidget(table, 3)
    tree = QTreeWidget()
    tree.setHeaderLabels(['Inventory'])
    parent = QTreeWidgetItem(tree, ['Lab'])
    QTreeWidgetItem(parent, ['Cluster A'])
    QTreeWidgetItem(parent, ['Cluster B'])
    tree.expandAll()
    results_layout.addWidget(tree, 2)
    tabs.addTab(results, 'Inventory')
    tabs.addTab(QWidget(), 'Activity')
    tabs.addTab(QWidget(), 'Restricted')
    tabs.setTabEnabled(2, False)
    layout.addWidget(tabs, 1)
    statuses = QHBoxLayout()
    for status, text in [('ok', 'Healthy'), ('warn', 'Review'), ('bad', 'Offline'), ('info', '4 services')]:
        statuses.addWidget(label(text, 'badge', status))
    layout.addLayout(statuses)
    layout.addWidget(label('Review network configuration before continuing.', 'banner', 'warn'))
    code = QPlainTextEdit('GET /api/inventory\n200 OK  |  26 nodes discovered')
    code.setProperty('lattice', 'code')
    code.setReadOnly(True)
    code.setMaximumHeight(74)
    layout.addWidget(code)
    progress = QProgressBar()
    progress.setValue(72)
    layout.addWidget(progress)
    window.resize(940, 850)
    address.setFocus()
    return window


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    warnings = []

    def message(_kind, _context, text):
        warnings.append(text)
        print(text)

    qInstallMessageHandler(message)
    app = QApplication([])
    for theme in ('light', 'dark'):
        apply_theme(app, theme)
        window = sample(theme)
        window.show()
        app.processEvents()
        shot = window.grab()
        assert not shot.isNull()
        tokens = json.loads((ROOT / 'project/tokens.json').read_text())
        colors = {t['name']: t['value'][theme] for t in tokens['color']['tokens']}
        # Check the actual rendered fills away from text, not just requested styles.
        pixels = shot.toImage()
        assert pixels.pixelColor(0, 0) == QColor(colors['bg'])
        for name, token in [('Connect', 'accent'), ('Unavailable', 'surface-sunken')]:
            button = window.findChild(QPushButton, name)
            point = button.mapTo(window, button.rect().topLeft())
            assert pixels.pixelColor(point.x() + 10, point.y() + button.height() // 2) == QColor(colors[token])
        assert QFontInfo(window.findChild(QPlainTextEdit).font()).fixedPitch()
        assert shot.save(str(args.output / f'lattice-{theme}.png'))
        window.close()
        window.deleteLater()
        app.processEvents()
    # Offscreen emits propagateSizeHints; parse/property warnings are real failures.
    assert not any('stylesheet' in s.lower() or 'unknown property' in s.lower() for s in warnings), warnings


if __name__ == '__main__':
    main()

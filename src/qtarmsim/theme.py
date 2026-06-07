# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#  This file is part of QtARMSim.                                         #
#                                                                         #
#  QtARMSim is free software: you can redistribute it and/or modify       #
#  it under the terms of the GNU General Public License as published by   #
#  the Free Software Foundation; either version 3 of the License, or      #
#  (at your option) any later version.                                    #
#                                                                         #
#  This program is distributed in the hope that it will be useful, but    #
#  WITHOUT ANY WARRANTY; without even the implied warranty of             #
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU      #
#  General Public License for more details.                               #
#                                                                         #
###########################################################################

from PySide6.QtCore import QByteArray, QFile, Qt
from PySide6.QtGui import QColor, QIcon, QPainter, QPalette, QPixmap
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import QApplication

SYSTEM = "system"
LIGHT = "light"
DARK = "dark"

_original_style: str = ""
_original_font_size: int = 0


def _dark_palette() -> QPalette:
    palette = QPalette()
    dark = QColor(53, 53, 53)
    darker = QColor(35, 35, 35)
    text = QColor(240, 240, 240)
    highlight = QColor(42, 130, 218)
    disabled = QColor(127, 127, 127)
    palette.setColor(QPalette.ColorRole.Window, dark)
    palette.setColor(QPalette.ColorRole.WindowText, text)
    palette.setColor(QPalette.ColorRole.Base, darker)
    palette.setColor(QPalette.ColorRole.AlternateBase, dark)
    palette.setColor(QPalette.ColorRole.ToolTipBase, darker)
    palette.setColor(QPalette.ColorRole.ToolTipText, text)
    palette.setColor(QPalette.ColorRole.Text, text)
    palette.setColor(QPalette.ColorRole.Button, dark)
    palette.setColor(QPalette.ColorRole.ButtonText, text)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, highlight)
    palette.setColor(QPalette.ColorRole.Highlight, highlight)
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled)
    palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled)
    return palette


_BREEZE_LIGHT_COLOR = b'#232629'
_BREEZE_DARK_COLOR = b'#eff0f1'
_ICON_SIZE = 22


def make_icon(resource_path: str, dark: bool) -> QIcon:
    """Load a Breeze SVG icon from Qt resources, recolored for dark mode if needed."""
    f = QFile(resource_path)
    if not f.open(QFile.OpenModeFlag.ReadOnly):
        return QIcon(resource_path)
    data: QByteArray = f.readAll()
    f.close()
    if dark:
        _ = data.replace(_BREEZE_LIGHT_COLOR, _BREEZE_DARK_COLOR)
    renderer = QSvgRenderer(data)
    pixmap = QPixmap(_ICON_SIZE, _ICON_SIZE)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    del painter
    return QIcon(pixmap)


def save_default_style() -> None:
    """Save the platform's default style name and font size. Call once at startup before apply_theme()."""
    global _original_style, _original_font_size
    app = QApplication.instance()
    if isinstance(app, QApplication):
        _original_style = app.style().objectName()
        _original_font_size = app.font().pointSize()


def get_original_font_size() -> int:
    """Return the system default font point size saved before any theme was applied."""
    return _original_font_size


def apply_theme(theme: str) -> None:
    """Apply the given color theme to the application.

    :param theme: One of SYSTEM, LIGHT, or DARK.
    """
    app = QApplication.instance()
    if not isinstance(app, QApplication):
        return
    if theme == DARK:
        app.setStyle("Fusion")
        app.setPalette(_dark_palette())
    elif theme == LIGHT:
        app.setStyle("Fusion")
        app.setPalette(app.style().standardPalette())
    else:
        app.setStyle(_original_style or "Fusion")
        app.setPalette(app.style().standardPalette())

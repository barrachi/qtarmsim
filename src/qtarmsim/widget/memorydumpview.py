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

from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Qt

from ..model.memorydumpproxymodel import MemoryDumpProxyModel


class _FontSyncDelegate(QtWidgets.QStyledItemDelegate):
    """Item delegate that applies the model's FontRole to the cell editor."""

    def createEditor(self, parent: QtWidgets.QWidget,  # pyright: ignore[reportIncompatibleMethodOverride]
                     option: QtWidgets.QStyleOptionViewItem,
                     index: QtCore.QModelIndex) -> QtWidgets.QWidget | None:
        editor = super().createEditor(parent, option, index)
        if editor is not None:
            font = index.data(Qt.ItemDataRole.FontRole)
            if isinstance(font, QtGui.QFont):
                editor.setFont(font)
        return editor


class MemoryDumpView(QtWidgets.QTableView):
    """QTableView for MemoryDumpProxyModel with CTRL+wheel and CTRL++/- font zoom."""

    def __init__(self, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setItemDelegate(_FontSyncDelegate(self))

    def _changeFontSize(self, increment: int) -> None:
        model = self.model()
        if isinstance(model, MemoryDumpProxyModel):
            model.changeFontSize(increment)
            self.resizeColumnsToContents()
            self.resizeRowsToContents()

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self._changeFontSize(event.angleDelta().y() // 120)
        else:
            super().wheelEvent(event)

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            if event.text() == '+':
                self._changeFontSize(1)
                return
            elif event.text() == '-':
                self._changeFontSize(-1)
                return
        super().keyPressEvent(event)

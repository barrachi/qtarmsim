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

from PySide6 import QtCore, QtWidgets, QtGui


class MyQTreeView(QtWidgets.QTreeView):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.geometry_updated = False
        self.header().setStretchLastSection(False)
        self.setUniformRowHeights(True)
        # Per-column width hints: maps column -> (sample_text, fixed_overhead_px)
        # When set, increaseFontSize computes widths from font metrics (O(1)).
        # When absent, it falls back to resizeColumnToContents.
        self._column_width_hints: dict[int, tuple[str, int]] = {}

    def updateGeometrySizes(self) -> None:
        self.geometry_updated = True
        self.resizeColumnToContents(0)
        self.resizeColumnToContents(1)
        width = self.columnWidth(0) + self.columnWidth(1)
        # If the vertical scroll bar is visible, add its width
        my_vertical_scrollbar = self.verticalScrollBar()
        if my_vertical_scrollbar.isVisible():
            width += my_vertical_scrollbar.width()
        self.setMinimumWidth(width)
        self.parent().setMinimumWidth(0)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        self.parent().parent().setMinimumWidth(0)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]

    def sizeHint(self) -> QtCore.QSize:
        """
        If there is no model yet, just return a 0x0 size.
        Else, compute the total width and height and set the minimum and maximum sizes of the parent dock widget
        """
        hint = super().sizeHint()
        if self.model() is None or self.model().rowCount(QtCore.QModelIndex()) == 0:
            return hint
        if not self.geometry_updated:
            self.updateGeometrySizes()
        hint.setWidth(self.minimumWidth())
        return hint

    def setColumnWidthHint(self, col: int, sample_text: str, fixed_overhead: int) -> None:
        """
        Register a width hint for a column so that increaseFontSize can recompute
        its width in O(1) from font metrics instead of re-measuring all rows.

        :param col: column index
        :param sample_text: the widest string that can appear in this column
        :param fixed_overhead: fixed extra pixels (indentation, padding) that do not scale with font
        """
        self._column_width_hints[col] = (sample_text, fixed_overhead)

    def increaseFontSize(self, inc: int) -> None:
        """
        Increases (decreases) the font size
        :param inc: number of points to increase the font
        """
        model = self.model()
        if model is None:
            return
        old_size = model.qFont.pointSize()  # pyright: ignore[reportAttributeAccessIssue]
        new_size = max(10, old_size + inc)
        if new_size == old_size:
            return
        # Wrap font change in layout signals so the view updates synchronously.
        # uniformRowHeights=True makes layoutChanged O(1) (only one row measured).
        model.layoutAboutToBeChanged.emit()  # pyright: ignore[reportAttributeAccessIssue]
        model.qFont.setPointSize(new_size)  # pyright: ignore[reportAttributeAccessIssue]
        model.qFontLast.setPointSize(new_size)  # pyright: ignore[reportAttributeAccessIssue]
        model.layoutChanged.emit()  # pyright: ignore[reportAttributeAccessIssue]
        # Column widths: O(1) from font metrics if hints set, else resizeColumnToContents
        if self._column_width_hints:
            fm = QtGui.QFontMetrics(model.qFont)  # pyright: ignore[reportAttributeAccessIssue]
            for col, (sample, overhead) in self._column_width_hints.items():
                self.setColumnWidth(col, fm.horizontalAdvance(sample) + overhead)
        else:
            for col in range(self.header().count()):
                self.resizeColumnToContents(col)
        width = sum(self.columnWidth(col) for col in range(self.header().count()))
        if self.verticalScrollBar().isVisible():
            width += self.verticalScrollBar().width()
        self.setMinimumWidth(width)
        self.parent().setMinimumWidth(0)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]
        self.parent().parent().setMinimumWidth(0)  # pyright: ignore[reportAttributeAccessIssue, reportOptionalMemberAccess]

    def keyPressEvent(self, event: QtGui.QKeyEvent):
        """
        Processes the CTRL++ and CTRL+- events
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            if event.text() == '+':
                self.increaseFontSize(1)
                return
            elif event.text() == '-':
                self.increaseFontSize(-1)
                return
        super().keyPressEvent(event)

    def wheelEvent(self, event: QtGui.QWheelEvent) -> None:
        """
        Processes the wheel event: zooms in and out whenever a CTRL+wheel event is triggered
        """
        if event.modifiers() == QtCore.Qt.KeyboardModifier.ControlModifier:
            self.increaseFontSize(int(event.angleDelta().y()) // 120)
        else:
            super().wheelEvent(event)

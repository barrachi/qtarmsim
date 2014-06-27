from PyQt4 import QtCore, QtGui

class MyQTreeView(QtGui.QTreeView):
    
    pass

    def sizeHint(self):
        """
        If there is no model yet, just return a 0x0 size.
        Else, compute the total width and set the minimum and maximum sizes of the parent dock widget
        """
        if self.model() == None:
            return QtCore.QSize(0,0)
        width=0
        my_vertical_scrollbar = self.verticalScrollBar()
        my_dock = self.parent().parent()
        # Compute width as the sum of the width of all the columns and an extra width
        if self.model():
            for i in range(self.model().rowCount(self.model().index(0,0,QtCore.QModelIndex()))):
                width += self.columnWidth(i)
        # @todo: the extra width should be obtained automatically
        width += 15
        # If the vertical scrollbar is visible, add its width
        if my_vertical_scrollbar.isVisible():
            width += my_vertical_scrollbar.width()
        my_dock.setMinimumWidth(width)
        return QtCore.QSize(width, 0)

#coding=utf8
import sys

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from utility.data_handler import TableHandler
from gui_impl.display_format import *

########################################################################
class MatrixModel(QAbstractTableModel):
    def __init__(self, parent=None):
        super(MatrixModel, self).__init__(parent)
        self.data = TableHandler()
        #signal&slot
        return

    def clearAll(self):
        self.data.clear()
        self.emit(SIGNAL('modelReset()'))

    def clearContent(self):
        self.data.clearContent()
        self.emit(SIGNAL('modelReset()'))

    def setSize(self, rows, col_headers):
        self.data.reset(rows, col_headers)
        self.emit(SIGNAL('modelReset()'))
        return

    def setTableContent(self, table_handler_inst):
        self.data.copyContent(table_handler_inst)
        self.emit(SIGNAL('modelReset()'))
        return

    def appendRows(self, n=1):
        self.data.addRows(n)
        self.emit(SIGNAL('rowsInserted(const QModelIndex &, int, int)'),
                  QModelIndex(), self.data.rows, self.data.rows+n-1)

    def deleteRows(self, row_list):
        self.data.delRows(row_list)
        self.emit(SIGNAL('modelReset()'))

    def getValue(self, row, column):
        return self.data.get(row, column)

    #-----------------------------------------------------------
    #pass

    #qt inherit & override
    #-----------------------------------------------------------
    def rowCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.data.rows

    def columnCount(self, QModelIndex_parent=None, *args, **kwargs):
        return self.data.columns

    def headerData(self, p_int, Qt_Orientation, int_role=None):
        if int_role == Qt.DisplayRole:
            if Qt_Orientation == Qt.Horizontal:
                return self.data.getHoriHeader(p_int)
            elif Qt_Orientation == Qt.Vertical:
                return str(p_int+1)
        return None

    def data(self, QModelIndex, int_role=None):
        if QModelIndex.isValid():
            if int_role == Qt.DisplayRole:
                return self.data.get(QModelIndex.row(), QModelIndex.column())
        return None

    def setData(self, QModelIndex, p_object, int_role=None):
        if int_role == Qt.EditRole:
            self.data.set(QModelIndex.row(), QModelIndex.column(), p_object)
        return True

    def flags(self, QModelIndex):
        return Qt.ItemIsEditable | super(MatrixModel, self).flags(QModelIndex)

#########################################################################
class AutoFormDelegate(QItemDelegate):
    def __init__(self, parent=None):
        super(AutoFormDelegate, self).__init__(parent)

    #qt inherit & override
    #------------------------------------------------------------
    def paint(self, QPainter, QStyleOptionViewItem, QModelIndex):
        try:
            col = QModelIndex.column()
            ##extremely dirty code, include 2 outer class implement details
            header = QModelIndex.model().data.hori_headers[col]
            ##1(data) 2(hori_headers)
        except:
            header = None

        QPainter.drawText(QStyleOptionViewItem.rect,
                          Qt.AlignCenter | Qt.TextWordWrap,
                          getFormedStr(header, QModelIndex.data()))

        self.drawFocus(QPainter, QStyleOptionViewItem, QStyleOptionViewItem.rect)
        return

#########################################################################

if __name__ == '__main__':
    import threading

    app = QApplication(sys.argv)

    tv = QTableView()
    dm = MatrixModel(tv)
    dele = AutoFormDelegate(tv)

    tv.setItemDelegate(dele)
    tv.setModel(dm)
    tv.show()

    dm.setSize(10, ['f', 's', 't'])

    sys.exit(app.exec_())
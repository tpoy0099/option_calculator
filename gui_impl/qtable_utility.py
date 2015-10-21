#coding=utf8
import pandas as PD
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from gui_impl.display_format import getFormedStr

#######################################################

def setWidgetItemContent(item, header, value):
    item.setText(getFormedStr(header, value))

def convert2WidgetItem(header, content):
    return QTableWidgetItem(getFormedStr(header, content))

def getCellContent(qtable, row, col):
    item = qtable.item(row, col)
    if item:
        return item.text()
    return None

###############################################################

def setTableProperty(qtable, headers):
    qtable.clear()
    qtable.setColumnCount(len(headers))
    qtable.setHorizontalHeaderLabels(headers)

def addTableWidgetRows(qtable, n=1):
    rows = qtable.rowCount()
    qtable.setRowCount(rows + n)
    cols = qtable.columnCount()
    for i in range(rows, rows+n):
        for c in range(0, cols):
            qtable.setItem(i, c, QTableWidgetItem(''))

def getSelectedRows(qtable):
    row_list = list()
    selected_range = qtable.selectedRanges()
    for rg in selected_range:
        row_list.extend(list(range(rg.topRow(), rg.bottomRow()+1)))
    return row_list

def getTableHeaders(qtable):
    headers = list()
    cols = qtable.columnCount()
    for c in range(0, cols):
        try:
            h_item = qtable.horizontalHeaderItem(c)
            headers.append(h_item.text())
        except:
            headers.append('')
    return headers

def setDataFrameIntoTable(df, qtable, clear_origins=True):
    if clear_origins:
        qtable.clearContents()
    rows = qtable.rowCount()
    qheaders = getTableHeaders(qtable)
    if df.shape[0] > rows:
        addTableWidgetRows(qtable, df.shape[0] - rows)
    for r in range(0, df.shape[0]):
        for h in df.columns:
            if h in qheaders:
                item = convert2WidgetItem(h, df[h].iat[r])
                c = qheaders.index(h)
                qtable.setItem(r, c, item)

def convertQTableToDataFrame(qtable):
    rows = qtable.rowCount()
    cols = qtable.columnCount()
    matrix_ls = list()
    for c in range(0, cols):
        col_items = list()
        for r in range(0, rows):
            text = getCellContent(qtable, r, c)
            if text:
                col_items.append(text)
            else:
                break
        matrix_ls.append(col_items)
    return PD.DataFrame(matrix_ls, columns=getTableHeaders(qtable))
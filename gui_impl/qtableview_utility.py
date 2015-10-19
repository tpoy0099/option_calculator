#coding=utf8
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def getSelectedRows(vtable):
    s_rows = list()
    for idx in vtable.selectedIndexes():
        s_rows.append(idx.row())
    return s_rows
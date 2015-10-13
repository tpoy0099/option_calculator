#coding=utf8
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ui_position_editor

class PosEditor(QDialog, ui_position_editor.Ui_position_editor_dialog):
    def __init__(self, parent=None):
        super(PosEditor, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        #signal&slot
        self.connect(self.cancel_button, SIGNAL("clicked()"), self.onCancelBtClicked)
        self.connect(self.save_button, SIGNAL("clicked()"), self.onSaveBtClicked)
        self.connect(self.reload_button, SIGNAL("clicked()"), self.onReloadBtClicked)
        #
        self.position_edit_table.setRowCount(3)
        self.position_edit_table.setColumnCount(3)
        self.position_edit_table.setItem(0,0, QTableWidgetItem('test'))

    def onCancelBtClicked(self):
        self.position_edit_table.clear()
        self.close()

    def onSaveBtClicked(self):
        item = self.position_edit_table.item(0,0)
        item.setText('alter')
        #self.position_edit_table.setItem(0,0, item)
        pass

    def onReloadBtClicked(self):
        self.position_edit_table.setItem(0,0, QTableWidgetItem('test'))
        item = self.position_edit_table.item(0,0)
        s = item.text()
        pass
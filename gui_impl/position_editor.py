#coding=utf8
from qt_ui.ui_position_editor import Ui_position_editor_dialog
from gui_impl.qt_mvc_impl import MatrixModel, AutoFormDelegate
from gui_impl.qtableview_utility import getSelectedRows
from utility.data_handler import TableHandler

from PyQt4.QtCore import *
from PyQt4.QtGui import *

##############################################################################
class PosEditor(QDialog, Ui_position_editor_dialog):
    EDIT_TABLE_HEADERS = ('group', 'code', 'dir', 'lots', 'open_price', 'margin', 'open_date')

    def __init__(self, parent=None):
        super(PosEditor, self).__init__(parent)
        self.setupUi(self)
        self.setModal(True)
        #signal&slot
        self.connect(self.cancel_button, SIGNAL("clicked()"), self.onCancelBtClicked)
        self.connect(self.save_button, SIGNAL("clicked()"), self.onSaveBtClicked)
        self.connect(self.reload_button, SIGNAL("clicked()"), self.onReloadBtClicked)
        self.connect(self.addrow_button, SIGNAL("clicked()"), self.onAddrowBtClicked)
        self.connect(self.delrows_button, SIGNAL("clicked()"), self.onDelRowBtClicked)
        #init mvc impl
        self.model = MatrixModel(self)
        self.delegate = AutoFormDelegate(self)
        self.position_edit_vtable.setItemDelegate(self.delegate)
        self.position_edit_vtable.setModel(self.model)
        #init data
        self.controler = None
        self.model.setSize(0, PosEditor.EDIT_TABLE_HEADERS)

    def setControler(self, ctl):
        self.controler = ctl

    #--------------------------------------------------
    def wakeupEditor(self):
        self.show()

    def setEditTableContent(self, table_hdl_inst):
        self.model.setTableContent(table_hdl_inst)

    #--------------------------------------------------
    def onAddrowBtClicked(self):
        self.model.appendRows()

    def onDelRowBtClicked(self):
        rows = getSelectedRows(self.position_edit_vtable)
        if rows:
            self.model.deleteRows(rows)

    def onCancelBtClicked(self):
        self.model.clearContent()
        self.close()

    @staticmethod
    def findInvalidRows(t_data=TableHandler()):
        invalid_rows = list()
        for r in range(0, t_data.rows):
            for h in ['group', 'code', 'dir', 'lots', 'open_price']:
                val = t_data.getByHeader(r, h)
                if val is None or val == '':
                    invalid_rows.append(r)
        return invalid_rows

    def onSaveBtClicked(self):
        rtn = QMessageBox.question(self, 'Confirm', 'Save position changes ?',
                                   QMessageBox.Yes, QMessageBox.No)
        if rtn == QMessageBox.Yes:
            data = TableHandler()
            data.copy(self.model.data)
            invalid_rows = PosEditor.findInvalidRows(data)
            if invalid_rows:
                data.delRows(invalid_rows)
            if data.rows > 0:
                self.controler.onEditorClickBtSaveAll(data)
                self.close()
            else:
                cf = QMessageBox.warning(self, 'Error',
                                         'position record invalid !', QMessageBox.Yes)
        return

    def onReloadBtClicked(self):
        rtn = QMessageBox.question(self, 'Confirm', 'Reload from position.csv ?',
                                   QMessageBox.Yes, QMessageBox.No)
        if rtn == QMessageBox.Yes:
            self.controler.onEditorClickBtReloadPosition()
        return

#######################################################################
if __name__ == '__main__':
    import sys, random
    app = QApplication(sys.argv)

    pedit = PosEditor()

    th = TableHandler()
    th.reset(10, PosEditor.EDIT_TABLE_HEADERS)
    for r in range(0, 10):
        for h in PosEditor.EDIT_TABLE_HEADERS:
            th.setByHeader(r, h, random.randint(0,10))

    pedit.wakeupEditor()

    sys.exit(app.exec_())

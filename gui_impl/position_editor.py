#coding=utf8

from qt_ui import ui_position_editor
from gui_impl.qt_mvc_impl import *
from gui_impl.qtableview_utility import *

##############################################################################
class PosEditor(QDialog, ui_position_editor.Ui_position_editor_dialog):
    EDIT_TABLE_HEADERS = ('group', 'code', 'dir', 'lots', 'open_price', 'margin')

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
        self.model.setSize(0, PosEditor.EDIT_TABLE_HEADERS)

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

    def onSaveBtClicked(self):
        #a = self.model.createIndex(0,0)
        #b= a.model().data.hori_headers
        pass

    def onReloadBtClicked(self):
        #self.position_edit_table.setItem(0,0, QTableWidgetItem('test'))
        #item = self.position_edit_table.item(0,0)
        #s = item.text()
        pass

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

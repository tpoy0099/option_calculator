# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'position_editor.ui'
#
# Created: Tue Oct 13 15:40:27 2015
#      by: PyQt4 UI code generator 4.10.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_position_editor_dialog(object):
    def setupUi(self, position_editor_dialog):
        position_editor_dialog.setObjectName(_fromUtf8("position_editor_dialog"))
        position_editor_dialog.resize(764, 484)
        self.gridLayout = QtGui.QGridLayout(position_editor_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.position_edit_table = QtGui.QTableWidget(position_editor_dialog)
        self.position_edit_table.setFrameShape(QtGui.QFrame.WinPanel)
        self.position_edit_table.setObjectName(_fromUtf8("position_edit_table"))
        self.position_edit_table.setColumnCount(0)
        self.position_edit_table.setRowCount(0)
        self.verticalLayout.addWidget(self.position_edit_table)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.reload_button = QtGui.QPushButton(position_editor_dialog)
        self.reload_button.setObjectName(_fromUtf8("reload_button"))
        self.horizontalLayout.addWidget(self.reload_button)
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.save_button = QtGui.QPushButton(position_editor_dialog)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.horizontalLayout.addWidget(self.save_button)
        self.cancel_button = QtGui.QPushButton(position_editor_dialog)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.horizontalLayout.addWidget(self.cancel_button)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(position_editor_dialog)
        QtCore.QMetaObject.connectSlotsByName(position_editor_dialog)

    def retranslateUi(self, position_editor_dialog):
        position_editor_dialog.setWindowTitle(_translate("position_editor_dialog", "positions", None))
        self.reload_button.setText(_translate("position_editor_dialog", "reload csv", None))
        self.save_button.setText(_translate("position_editor_dialog", "save all", None))
        self.cancel_button.setText(_translate("position_editor_dialog", "cancel", None))


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'position_editor.ui'
#
# Created: Mon Oct 19 21:28:50 2015
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
        position_editor_dialog.resize(850, 600)
        self.gridLayout = QtGui.QGridLayout(position_editor_dialog)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.position_edit_vtable = QtGui.QTableView(position_editor_dialog)
        self.position_edit_vtable.setAlternatingRowColors(True)
        self.position_edit_vtable.setObjectName(_fromUtf8("position_edit_vtable"))
        self.horizontalLayout.addWidget(self.position_edit_vtable)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.addrow_button = QtGui.QPushButton(position_editor_dialog)
        self.addrow_button.setObjectName(_fromUtf8("addrow_button"))
        self.verticalLayout_3.addWidget(self.addrow_button)
        self.delrows_button = QtGui.QPushButton(position_editor_dialog)
        self.delrows_button.setObjectName(_fromUtf8("delrows_button"))
        self.verticalLayout_3.addWidget(self.delrows_button)
        self.verticalLayout_2.addLayout(self.verticalLayout_3)
        spacerItem = QtGui.QSpacerItem(20, 50, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout_2.addItem(spacerItem)
        self.reload_button = QtGui.QPushButton(position_editor_dialog)
        self.reload_button.setObjectName(_fromUtf8("reload_button"))
        self.verticalLayout_2.addWidget(self.reload_button)
        spacerItem1 = QtGui.QSpacerItem(20, 30, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.MinimumExpanding)
        self.verticalLayout_2.addItem(spacerItem1)
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.save_button = QtGui.QPushButton(position_editor_dialog)
        self.save_button.setObjectName(_fromUtf8("save_button"))
        self.verticalLayout.addWidget(self.save_button)
        self.cancel_button = QtGui.QPushButton(position_editor_dialog)
        self.cancel_button.setObjectName(_fromUtf8("cancel_button"))
        self.verticalLayout.addWidget(self.cancel_button)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        self.horizontalLayout.addLayout(self.verticalLayout_2)
        self.gridLayout.addLayout(self.horizontalLayout, 0, 0, 1, 1)

        self.retranslateUi(position_editor_dialog)
        QtCore.QMetaObject.connectSlotsByName(position_editor_dialog)

    def retranslateUi(self, position_editor_dialog):
        position_editor_dialog.setWindowTitle(_translate("position_editor_dialog", "positions", None))
        self.addrow_button.setText(_translate("position_editor_dialog", "add row", None))
        self.delrows_button.setText(_translate("position_editor_dialog", "delete", None))
        self.reload_button.setText(_translate("position_editor_dialog", "reload csv", None))
        self.save_button.setText(_translate("position_editor_dialog", "save all", None))
        self.cancel_button.setText(_translate("position_editor_dialog", "cancel", None))


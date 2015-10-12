# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'opt.ui'
#
# Created: Fri Oct  9 10:35:01 2015
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(824, 580)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.etf_name_label = QtGui.QLabel(self.centralwidget)
        self.etf_name_label.setObjectName(_fromUtf8("etf_name_label"))
        self.horizontalLayout.addWidget(self.etf_name_label)
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.horizontalLayout.addWidget(self.line)
        self.etf_openprice_label = QtGui.QLabel(self.centralwidget)
        self.etf_openprice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.etf_openprice_label.setObjectName(_fromUtf8("etf_openprice_label"))
        self.horizontalLayout.addWidget(self.etf_openprice_label)
        self.etf_highprice_label = QtGui.QLabel(self.centralwidget)
        self.etf_highprice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.etf_highprice_label.setObjectName(_fromUtf8("etf_highprice_label"))
        self.horizontalLayout.addWidget(self.etf_highprice_label)
        self.etf_lowprice_label = QtGui.QLabel(self.centralwidget)
        self.etf_lowprice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.etf_lowprice_label.setObjectName(_fromUtf8("etf_lowprice_label"))
        self.horizontalLayout.addWidget(self.etf_lowprice_label)
        self.etf_lastprice_label = QtGui.QLabel(self.centralwidget)
        self.etf_lastprice_label.setAlignment(QtCore.Qt.AlignCenter)
        self.etf_lastprice_label.setObjectName(_fromUtf8("etf_lastprice_label"))
        self.horizontalLayout.addWidget(self.etf_lastprice_label)
        self.update_time_label = QtGui.QLabel(self.centralwidget)
        self.update_time_label.setAlignment(QtCore.Qt.AlignCenter)
        self.update_time_label.setObjectName(_fromUtf8("update_time_label"))
        self.horizontalLayout.addWidget(self.update_time_label)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.positions_table = QtGui.QTableWidget(self.centralwidget)
        self.positions_table.setFrameShape(QtGui.QFrame.WinPanel)
        self.positions_table.setEditTriggers(QtGui.QAbstractItemView.DoubleClicked|QtGui.QAbstractItemView.EditKeyPressed)
        self.positions_table.setObjectName(_fromUtf8("positions_table"))
        self.positions_table.setColumnCount(0)
        self.positions_table.setRowCount(0)
        self.verticalLayout.addWidget(self.positions_table)
        self.portfolio_table = QtGui.QTableWidget(self.centralwidget)
        self.portfolio_table.setFrameShape(QtGui.QFrame.WinPanel)
        self.portfolio_table.setObjectName(_fromUtf8("portfolio_table"))
        self.portfolio_table.setColumnCount(0)
        self.portfolio_table.setRowCount(0)
        self.verticalLayout.addWidget(self.portfolio_table)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.fresh_quotes_button = QtGui.QPushButton(self.centralwidget)
        self.fresh_quotes_button.setObjectName(_fromUtf8("fresh_quotes_button"))
        self.gridLayout.addWidget(self.fresh_quotes_button, 0, 0, 1, 1)
        self.greeks_sensibility_button = QtGui.QPushButton(self.centralwidget)
        self.greeks_sensibility_button.setObjectName(_fromUtf8("greeks_sensibility_button"))
        self.gridLayout.addWidget(self.greeks_sensibility_button, 1, 1, 1, 1)
        self.reload_position_button = QtGui.QPushButton(self.centralwidget)
        self.reload_position_button.setObjectName(_fromUtf8("reload_position_button"))
        self.gridLayout.addWidget(self.reload_position_button, 1, 0, 1, 1)
        self.greeks_x_axis_combobox = QtGui.QComboBox(self.centralwidget)
        self.greeks_x_axis_combobox.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.greeks_x_axis_combobox.setFrame(True)
        self.greeks_x_axis_combobox.setObjectName(_fromUtf8("greeks_x_axis_combobox"))
        self.greeks_x_axis_combobox.addItem(_fromUtf8(""))
        self.greeks_x_axis_combobox.addItem(_fromUtf8(""))
        self.greeks_x_axis_combobox.addItem(_fromUtf8(""))
        self.greeks_x_axis_combobox.addItem(_fromUtf8(""))
        self.gridLayout.addWidget(self.greeks_x_axis_combobox, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 824, 26))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuAbout = QtGui.QMenu(self.menubar)
        self.menuAbout.setObjectName(_fromUtf8("menuAbout"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.menuAbout.addAction(self.actionAbout)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.etf_name_label.setText(_translate("MainWindow", "50ETF 510050.SH (O/H/L/C)", None))
        self.etf_openprice_label.setText(_translate("MainWindow", "0", None))
        self.etf_highprice_label.setText(_translate("MainWindow", "0", None))
        self.etf_lowprice_label.setText(_translate("MainWindow", "0", None))
        self.etf_lastprice_label.setText(_translate("MainWindow", "0", None))
        self.update_time_label.setText(_translate("MainWindow", "N/A", None))
        self.positions_table.setSortingEnabled(False)
        self.fresh_quotes_button.setText(_translate("MainWindow", "fresh quotes", None))
        self.greeks_sensibility_button.setText(_translate("MainWindow", "greeks sensibility", None))
        self.reload_position_button.setText(_translate("MainWindow", "reload position", None))
        self.greeks_x_axis_combobox.setItemText(0, _translate("MainWindow", "by assert price", None))
        self.greeks_x_axis_combobox.setItemText(1, _translate("MainWindow", "by volatility", None))
        self.greeks_x_axis_combobox.setItemText(2, _translate("MainWindow", "by time", None))
        self.greeks_x_axis_combobox.setItemText(3, _translate("MainWindow", "all of three", None))
        self.menuAbout.setTitle(_translate("MainWindow", "about", None))
        self.actionAbout.setText(_translate("MainWindow", "about", None))


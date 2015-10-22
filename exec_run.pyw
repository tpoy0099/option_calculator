#coding=utf8
import sys
from PyQt4.QtGui import *
from gui_impl.mw_calculator import OptionCalculator

#########################################################
app = QApplication(sys.argv)

#app.setStyleSheet('QTableView{background-color: #CCE8CF}')

mw = OptionCalculator()
mw.start()

app.exec_()
#coding=utf8
import sys

from PyQt4.QtGui import *

from gui_impl.mw_calculator import OptionCalculator

app = QApplication(sys.argv)
mw = OptionCalculator()
app.exec_()
mw.quit()
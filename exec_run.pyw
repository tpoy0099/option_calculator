#coding=utf8
import sys
from PyQt4.QtGui import *
from qt_calculator import OptionCalculator

app = QApplication(sys.argv)
mw = OptionCalculator()
app.exec_()
mw.quit()
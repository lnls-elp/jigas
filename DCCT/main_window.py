#!/usr/bin/python3
import sys
from PyQt5 import QtGui, QtCore, QtWidgets, uic

class Window(QtWidgets.QWizard):

    def __init__(self):
        super(Window, self).__init__()
        uic.loadUi('wizard.ui', self)
        self.show()

app = QtWidgets.QApplication(sys.argv)
GUI = Window()
sys.exit(app.exec_())

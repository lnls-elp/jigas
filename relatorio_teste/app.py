#!/usr/bin/python3
from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.uic import loadUiType
import sys

UI_PATH = 'gui.ui'
Ui_Class, base = loadUiType(UI_PATH)

class Report(QWidget, Ui_Class):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)

        self._initialize_signals()

    """*************************************************
    *************** GUI Initialization *****************
    *************************************************"""
    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbHradc.clicked.connect(self._get_hradc_report)
        self.pbCalibHradc.clicked.connect(self._get_hradc_calib_report)
        self.pbDcct.clicked.connect(self._get_dcct_report)
        self.pbRack.clicked.connect(self._get_rack_report)
        self.pbPowerModule.clicked.connect(self._get_pm_report)
        self.pbUdc.clicked.connect(self._get_udc_report)
        self.pbPowerSupply.clicked.connect(self._get_ps_report)
        self.pbBurnIn.clicked.connect(self._get_burn_in_report)

    @pyqtSlot()
    def _get_hradc_report(self):
        pass

    @pyqtSlot()
    def _get_hradc_calib_report(self):
        pass

    @pyqtSlot()
    def _get_dcct_report(self):
        pass

    @pyqtSlot()
    def _get_rack_report(self):
        pass

    @pyqtSlot()
    def _get_pm_report(self):
        pass

    @pyqtSlot()
    def _get_udc_report(self):
        pass

    @pyqtSlot()
    def _get_ps_report(self):
        pass

    @pyqtSlot()
    def _get_burn_in_report(self):
        pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Report()
    gui.show()
    sys.exit(app.exec_()):

#!/usr/bin/python3
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.uic import loadUiType
from converter import Converter
import sys

UI_PATH = 'gui.ui'
Ui_Class, base = loadUiType(UI_PATH)

class Report(QWidget, Ui_Class):

    def __init__(self, parent=None):
        QWidget.__init__(self, parent)
        self.setupUi(self)
        self._initialize_signals()
        self._conv = Converter()

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
        self.pbBurnIn.clicked.connect(self._get_ps_report)

    @pyqtSlot()
    def _get_hradc_report(self):
        url = '/HradcReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbHradc.setEnabled(False)
        self.pbHradc.setText("Aguarde!")
        self._conv.start()

    @pyqtSlot()
    def _get_hradc_calib_report(self):
        url = '/HradcCalibReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbCalibHradc.setText("Aguarde!")
        self.pbCalibHradc.setEnabled(False)
        self._conv.start()

    @pyqtSlot()
    def _get_dcct_report(self):
        url = '/DcctReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbDcct.setText("Aguarde!")
        self.pbDcct.setEnabled(False)
        self._conv.start()

    @pyqtSlot()
    def _get_rack_report(self):
        url = '/RackReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbRack.setText("Aguarde!")
        self.pbRack.setEnabled(False)
        self._conv.start()

    @pyqtSlot()
    def _get_pm_report(self):
        url = '/PowerModuleReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbPowerModule.setText("Aguarde!")
        self.pbPowerModule.setEnabled(False)
        self._conv.start()

    @pyqtSlot()
    def _get_udc_report(self):
        url = '/UdcReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbUdc.setText("Aguarde!")
        self.pbUdc.setEnabled(False)
        self._conv.start()

    @pyqtSlot()
    def _get_ps_report(self):
        url = '/PowerSupplyReport'
        self._conv.resource = url
        self._conv.conversion_complete.connect(self._clear)
        self.pbPowerSupply.setText("Aguarde!")
        self.pbPowerSupply.setEnabled(False)
        self._conv.start()

    @pyqtSlot(bool)
    def _clear(self, status):
        self._conv.conversion_complete.disconnect()
        self.pbHradc.setEnabled(True)
        self.pbCalibHradc.setEnabled(True)
        self.pbDcct.setEnabled(True)
        self.pbRack.setEnabled(True)
        self.pbPowerModule.setEnabled(True)
        self.pbPowerSupply.setEnabled(True)
        self.pbUdc.setEnabled(True)
        self.pbBurnIn.setEnabled(True)
        self.pbHradc.setText("HRADC")
        self.pbCalibHradc.setText("HRADC\nCalibração")
        self.pbDcct.setText("DCCT")
        self.pbRack.setText("Bastidor")
        self.pbPowerModule.setText("Módulo\nPotência")
        self.pbPowerSupply.setText("Fonte\nCompleta")
        self.pbUdc.setText("UDC")
        self.pbBurnIn.setText("Burn-In")

        if status:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Sucesso")
            msg.setInformativeText("Sucesso: Veja a pasta relatorios")
            msg.setWindowTitle("Sucesso")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("ERRO")
            msg.setInformativeText("ERRO: Dados Não existem")
            msg.setWindowTitle("ERRO")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = Report()
    gui.show()
    sys.exit(app.exec_())

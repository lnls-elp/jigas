#!/usr/bin/python3
import sys
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from dmreader import *
from dcctdata import *

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class DCCTWindow(QWizard, Ui_Class):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)
        #super(DCCTWindow, self).__init__(parent)
        #uic.loadUi('wizard.ui', self)

        self._SERIAL_BAUDRATE = 115200

        self._initialize_widgets()
        self._initialize_signals()
        self._initialize_wizard_buttons()
        self._block_buttons()

        self._dcct = DCCT()
        self._log = DCCTLog()


    @pyqtSlot()
    def _read_serial_number(self):
        data = ReadDataMatrix()
        if data == None:
            self.lbReadSerialStatus.setText("<p color:'red'><b>ERRO. Digite Manualmente!</b><p/>")
        else:
            self._dcct.numero_serie = data
            self._dcct.add_dcct() ## Remove this. Use only when test finish
            self.leSerialNumber.setText(str(data))
        print("Read serial number")

    @pyqtSlot()
    def _treat_read_serial_edit(self):
        if self.cbEnableSerialNumberEdit.isChecked():
            self.leSerialNumber.setReadOnly(False)
        else:
            self.leSerialNumber.setReadOnly(True)

    @pyqtSlot()
    def _connect_serial_port(self):
        self.PageConnectSerialPort.wizard().button(self.NextButton).setEnabled(True)
        #TODO: Connect and test serial port

    @pyqtSlot()
    def _start_test_sequence(self):
        self.PageStartTest.wizard().button(self.NextButton).setEnabled(True)
        #TODO: Start test sequence thread

    @pyqtSlot()
    def _submit_test_report(self):
        self.PageSubmitReport.wizard().button(self.FinishButton).setEnabled(True)
        #TODO: Submit report to server

    @pyqtSlot()
    def _finish_wizard_execution(self):
        # Qdo usuario clica em cancel ou em finish
        print("*****TERMINOU******")

    def _initialize_widgets(self):
        """ Initial widgets configuration """
        self.leBaudrate.setText(str(self._SERIAL_BAUDRATE))
        self.leBaudrate.setReadOnly(True)
        self.leSerialNumber.setReadOnly(True)
        self.lbReadSerialStatus.setText("")

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbReadSerialNumber.clicked.connect(self._read_serial_number)
        self.cbEnableSerialNumberEdit.stateChanged.connect(self._treat_read_serial_edit)
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        #self.pbSubmitTestReport.clicked.connect(self._submit_test_report)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageIntro.setButtonText(self.NextButton, "Próximo")
        self.PageIntro.setButtonText(self.BackButton, "Anterior")
        self.PageIntro.setButtonText(self.CancelButton, "Cancelar")

        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectDCCT.setButtonText(self.NextButton, "Próximo")
        self.PageConnectDCCT.setButtonText(self.BackButton, "Anterior")
        self.PageConnectDCCT.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectSerialPort.setButtonText(self.NextButton, "Próximo")
        self.PageConnectSerialPort.setButtonText(self.BackButton, "Anterior")
        self.PageConnectSerialPort.setButtonText(self.CancelButton, "Cancelar")

        self.PageStartTest.setButtonText(self.NextButton, "Próximo")
        self.PageStartTest.setButtonText(self.BackButton, "Anterior")
        self.PageStartTest.setButtonText(self.CancelButton, "Cancelar")

        self.PageSubmitReport.setButtonText(self.BackButton, "Anterior")
        self.PageSubmitReport.setButtonText(self.CancelButton, "Cancelar")
        self.PageSubmitReport.setButtonText(self.FinishButton, "Novo Teste")

    def _block_buttons(self):
        self.PageSubmitReport.wizard().button(self.FinishButton).setEnabled(False)

class Test(QWizardPage):
    def __init__(self, parent=None):
        super(Test, self).__init__(parent)

    def nextId(self):
        return DCCTWindow.PageStartTest

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DCCTWindow()
    gui.show()
    sys.exit(app.exec_())

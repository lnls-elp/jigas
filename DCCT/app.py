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
        #self.PageStartTest.wizard().button(self.NextButton).setEnabled(True)
        #TODO: Start test sequence thread
        pass

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
        self.PageSubmitReport.setButtonText(self.NextButton, "Novo Teste")

    def _submit_test_report(self):
        #TODO: Submit report to server
        #dcct = self._dcct.add_dcct()
        #log = self._log.add_log_dcct()
        pass

    ## Initialize Pages for wizard
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_dcct(self):
        pass

    def _initialize_page_connect_serial_port(self):
        pass

    def _initialize_page_start_test(self):
        pass

    def _initialize_page_submit_report(self):
        self._submit_test_report()

    #QWizardPage methods - Override
    def initializePage(self, page):
        if page == 0:
            self._initialize_intro_page()
            print(self.currentId())

        elif page == 1:
            self._initialize_page_serial_number()
            print(self.currentId())

        elif page == 2:
            self._initialize_page_connect_dcct()
            print(self.currentId())

        elif page == 3:
            self._initialize_page_connect_serial_port()
            print(self.currentId())

        elif page == 4:
            self._initialize_page_start_test()
            print(self.currentId())

        elif page == 5:
            self._initialize_page_submit_report()
            print(self.currentId())
        else:
            pass

    def nextId(self):
        current_id = self.currentId()
        if current_id == 5:
            return 1
        else:
            return current_id + 1

    def isComplete(self):
        return False

    def isFinalPage(self):
        return False

    def validateCurrentPage(self):
        if self.currentPage == 1:
            return False
        return True

    def next(self):
        if self.currentId() == 5:
            while self.currentId() != 1:
                self.back()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DCCTWindow()
    gui.show()
    sys.exit(app.exec_())

#!/usr/bin/python3
import sys
import glob
import serial
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from dccttest import DCCTTest
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

        self._test = {}
        self._test['serial_port_test']   = False
        self._test['final']              = False

        self._list_serial_ports()
        self._serial_port = serial.Serial()


    @pyqtSlot()
    def _read_serial_number(self):
        data = ReadDataMatrix()
        if data == None:
            self.lbReadSerialStatus.setText("<p color:'red'><b>ERRO. Digite Manualmente!</b><p/>")
        else:
            self._dcct.numero_serie = data
            self._log.numero_serie_dcct = data
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
        com = str(self.comboComPort.currentText())
        baud = int(self.leBaudrate.text())
        self._serial_port.baudrate = baud
        self._serial_port.port = com
        self._serial_port.open()
        if self._serial_port.is_open:
            self.pbConnectSerialPort.setEnabled(False)
            self.completeChanged.emit()

    @pyqtSlot()
    def _start_test_sequence(self):
        #self.test_thread = DCCTtest()
        #self.test_thread.test_complete.connect(self._finish_test)
        #self.test_thread.start()
        #TODO: Start test sequence thread
        pass

    @pyqtSlot()
    def _finish_wizard_execution(self):
        # Qdo usuario clica em cancel ou em finish
        print("*****TERMINOU******")

    @pyqtSlot(dict)
    def _test_finished(self, test_result):
        pass

    def _initialize_widgets(self):
        """ Initial widgets configuration """
        self.leBaudrate.setText(str(self._SERIAL_BAUDRATE))
        self.leBaudrate.setReadOnly(True)
        self.leSerialNumber.setReadOnly(True)
        self.leSerialNumber.clear()
        self.lbReadSerialStatus.clear()
        self.cbEnableSerialNumberEdit.setChecked(False)
        self.lbStatusComunicacao.setText("...")
        self.lbStatusAuxSupply.setText("...")
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult.setText("Aguarde...")
        self.teTestReport.clear()
        self.lbStatusSubmitRequest.setText("Aguarde...")

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbReadSerialNumber.clicked.connect(self._read_serial_number)
        self.cbEnableSerialNumberEdit.stateChanged.connect(self._treat_read_serial_edit)
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        #self.pbSubmitTestReport.clicked.connect(self._submit_test_report)
        self.finished.connect(self._finish_wizard_execution)
        self.completeChanged = pyqtSignal()

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

    def _list_serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsuported platform')

        #result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.comboComPort.addItem(port)
            except (OSError, serial.SerialException):
                pass
        #return result

    ## Initialize Pages for wizard
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_dcct(self):
        pass

    def _initialize_page_connect_serial_port(self):
        print("Teste porta serial!")

    def _initialize_page_start_test(self):
        print("Start test iniciado!")

    def _initialize_page_submit_report(self):
        print("Submit teste!")
        self._submit_test_report()

    ## validate pages for wizard
    def _validate_intro_page(self):
        if self._serial_port.is_open:
            return True
        return False

    def _validate_page_serial_number(self):
        serial = self.leSerialNumber.text()
        if serial is not "":
            try:
                self._dcct.numero_serie = int(serial)
                self._log.numero_serie_dcct = int(serial)
                return True
            except ValueError:
                pass
        return False

    def _validate_page_connect_dcct(self):
        return True

    def _validate_page_connect_serial_port(self):
        print('Validate Conn Serial')
        return True

    def _validate_page_start_test(self):
        print('Validate Start Test')
        return True

    def _validate_page_submit_report(self):
        print('Validate Submit')
        self._initialize_widgets()
        for item in self._test:
            self._test[item] = False
        while self.currentId() is not 1:
            self.back()
        return False

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

# Last minute validation (before the next page is showed)
    def validateCurrentPage(self):
        current_id = self.currentId()
        if current_id == 0:
            return self._validate_intro_page()

        elif current_id == 1:
            print("Valida 1")
            return self._validate_page_serial_number()

        elif current_id == 2:
            print("Valida 2")
            return self._validate_page_connect_dcct()

        elif current_id == 3:
            print("Valida 3")
            return self._validate_page_connect_serial_port()

        elif current_id == 4:
            print("Valida 4")
            return self._validate_page_start_test()

        elif current_id == 5:
            print("Valida 5")
            return self._validate_page_submit_report()

        else:
            return True

#    def nextId(self):
#        current_id = self.currentId()
#        if current_id == 5:
#            return 1
#        else:
#            return current_id + 1

    def isComplete():
        return False

    def next(self):
        if self.currentId() == 5:
            while self.currentId() != 1:
                self.back()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DCCTWindow()
    gui.show()
    sys.exit(app.exec_())

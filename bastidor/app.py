#!/usr/bin/python3
import sys
import glob
import serial
import simplejson as json
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from racktest import RackTest
#from dmreader import *
from rackdata import *
from webrequest import *

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class RackWindow(QWizard, Ui_Class):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)
        #super(DCCTWindow, self).__init__(parent)
        #uic.loadUi('wizard.ui', self)

        self._SERIAL_BAUDRATE = 115200

        self._rack = Rack()
        self._log = RackLog()

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False
        self._test_final_status = False

        self._test_thread = RackTest()
        self._web_request = WebRequest()

        self._initialize_widgets()
        self._initialize_signals()
        self._initialize_wizard_buttons()

    """*************************************************
    *************** GUI Initialization *****************
    *************************************************"""
    def _initialize_widgets(self):
        """ Initial widgets configuration """
        self.leBaudrate.setText(str(self._SERIAL_BAUDRATE))
        self.leBaudrate.setReadOnly(True)
        self.leSerialNumber.setReadOnly(True)
        self.leSerialNumber.clear()
        self.lbReadSerialStatus.clear()
        self.cbEnableSerialNumberEdit.setChecked(False)
        self.lbStatusComunicacao.setText("...")
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
        self.pbCommunicationTest.clicked.connect(self._communication_test)
        #self._web_request.server_response.connect(self._treat_server_response)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageIntro.setButtonText(self.NextButton, "Próximo")
        self.PageIntro.setButtonText(self.BackButton, "Anterior")
        self.PageIntro.setButtonText(self.CancelButton, "Cancelar")

        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectRack.setButtonText(self.NextButton, "Próximo")
        self.PageConnectRack.setButtonText(self.BackButton, "Anterior")
        self.PageConnectRack.setButtonText(self.CancelButton, "Cancelar")

        self.PageTestSerialPort.setButtonText(self.NextButton, "Próximo")
        self.PageTestSerialPort.setButtonText(self.BackButton, "Anterior")
        self.PageTestSerialPort.setButtonText(self.CancelButton, "Cancelar")

        self.PageStartTest.setButtonText(self.NextButton, "Próximo")
        self.PageStartTest.setButtonText(self.BackButton, "Anterior")
        self.PageStartTest.setButtonText(self.CancelButton, "Cancelar")

        self.PageSubmitReport.setButtonText(self.BackButton, "Anterior")
        self.PageSubmitReport.setButtonText(self.CancelButton, "Cancelar")
        self.PageSubmitReport.setButtonText(self.NextButton, "Novo Teste")

    """*************************************************
    ************* System Initialization ****************
    *************************************************"""
    def _list_serial_ports(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsuported platform')

        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                self.comboComPort.addItem(port)
            except (OSError, serial.SerialException):
                pass

    def _restart_variables(self):
        self._serial_port_status = False
        self._test_serial_port_status = False
        self._test_final_status = False

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_rack(self):
        pass

    def _initialize_page_test_serial_port(self):
        print("Teste porta serial!")

    def _initialize_page_start_test(self):
        print("Start test iniciado!")

    def _initialize_page_submit_report(self):
        self._web_request.device = self._rack
        self._web_request.log = self._log
        self._web_request.server_response.connect(self._treat_server_response)
        self._web_request.start()

    """*************************************************
    ************** Pages Validation ********************
    *************************************************"""
    def _validate_intro_page(self):
        if self._serial_port_status:
            return True
        return False

    def _validate_page_serial_number(self):
        serial = self.leSerialNumber.text()
        if serial is not "":
            try:
                self._rack.serial_number = int(serial)
                self._log.serial_number_rack = int(serial)
                return True
            except ValueError:
                pass
        return False

    def _validate_page_connect_rack(self):
        return True

    def _validate_page_test_serial_port(self):
        if self._test_serial_port_status:
            return True
        return False

    def _validate_page_start_test(self):
        if self._test_final_status:
            return True
        return False

    def _validate_page_submit_report(self):
        print('Validate Submit')
        self._initialize_widgets()
        self._restart_variables
        while self.currentId() is not 1:
            self.back()
        return False

    """*************************************************
    *********** Default Methods (Wizard) ***************
    *************************************************"""
    def initializePage(self, page):
        if page == 0:
            self._initialize_intro_page()
            print(self.currentId())

        elif page == 1:
            self._initialize_page_serial_number()
            print(self.currentId())

        elif page == 2:
            self._initialize_page_connect_rack()
            print(self.currentId())

        elif page == 3:
            self._initialize_page_test_serial_port()
            print(self.currentId())

        elif page == 4:
            self._initialize_page_start_test()
            print(self.currentId())

        elif page == 5:
            self._initialize_page_submit_report()
            print(self.currentId())
        else:
            pass

    def validateCurrentPage(self):
        current_id = self.currentId()
        if current_id == 0:
            return self._validate_intro_page()

        elif current_id == 1:
            print("Valida 1")
            return self._validate_page_serial_number()

        elif current_id == 2:
            print("Valida 2")
            return self._validate_page_connect_rack()

        elif current_id == 3:
            print("Valida 3")
            return self._validate_page_test_serial_port()

        elif current_id == 4:
            print("Valida 4")
            return self._validate_page_start_test()

        elif current_id == 5:
            print("Valida 5")
            return self._validate_page_submit_report()

        else:
            return True

    def next(self):
        if self.currentId() == 5:
            while self.currentId() != 1:
                self.back()

    """*************************************************
    ******************* PyQt Slots *********************
    *************************************************"""
    @pyqtSlot()
    def _read_serial_number(self):
        data = ReadDataMatrix()
        if data == None:
            self.lbReadSerialStatus.setText("<p color:'red'><b>ERRO. Digite Manualmente!</b><p/>")
        else:
            self._rack.serial_number = data
            self._log.serial_number_rack = data
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
        self._test_thread.baudrate = baud
        self._test_thread.comport  = com
        self._serial_port_status = self._test_thread.open_serial_port()
        if self._serial_port_status:
            self.pbConnectSerialPort.setEnabled(False)

    @pyqtSlot()
    def _communication_test(self):
        result = self._test_thread.test_communication()
        if result:
            self.lbStatusComunicacao.setText("<p color:'green'>OK</p>")
        else:
            self.lbStatusComunicacao.setText("<p color:'red'>Falha</p>")
        self._test_serial_port_status = True


    @pyqtSlot()
    def _start_test_sequence(self):
        self._test_thread.test_complete.connect(self._test_finished)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass

    @pyqtSlot(dict)
    def _test_finished(self, test_result):
        print(test_result)
        self._log.test_result        = test_result['result']
        self._log.iout0              = test_result['iout'][0]
        self._log.iout1              = test_result['iout'][1]
        self._log.iout2              = test_result['iout'][2]
        self._log.iout3              = test_result['iout'][3]
        self._log.delta_iout0        = test_result['iout'][4]
        self._log.delta_iout1        = test_result['iout'][5]
        self._log.delta_iout2        = test_result['iout'][6]
        self._log.delta_iout3        = test_result['iout'][7]
        self._log.details            = test_result['details']
        self._log.serial_number_rack = self._rack.serial_number
        print(self._log.data)
        self.lbTestStatus.setText("Teste Finalizado!")
        self.lbTestResult.setText(self._log.test_result)
        self._test_final_status = True

    @pyqtSlot(dict, dict)
    def _treat_server_response(self, device_res, log_res):
        res_key = 'StatusCode'
        err_key = 'error'
        if res_key in device_res.keys() and res_key in log_res.keys():
            self.lbStatusSubmitRequest.setText('Sucesso!!!')
            self.lbRespDevice.setText(device_res['Message'])
            self.lbRespLog.setText(log_res['Message'])
        else:
            self.lbStatusSubmitRequest.setText('Falha!!!')
            self.lbRespDevice.setText(str(device_res))
            self.lbRespLog.setText(str(log_res))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = RackWindow()
    gui.show()
    sys.exit(app.exec_())
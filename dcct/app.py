#!/usr/bin/python3
import sys
import glob
import serial
import simplejson as json
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from dccttest import DCCTTest
#from dmreader import *
from dcctdata import *
from webrequest import *

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class DCCTWindow(QWizard, Ui_Class):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)
        #super(DCCTWindow, self).__init__(parent)
        #uic.loadUi('wizard.ui', self)

        self._SERIAL_BAUDRATE = 115200

        self._dcct = DCCT()
        self._log = DCCTLog()

        self._list_serial_ports()
        self._serial_port_status = False
        self._web_request_status = False

        self._test_thread = DCCTTest()
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

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
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
        self._web_request.device = self._dcct
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
                self._dcct.serial_number = int(serial)
                self._log.serial_number_dcct = int(serial)
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
            self._dcct.serial_number = data
            self._log.serial_number_dcct = data
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
        if result[0]:
            self.lbStatusComunicacao.setText("<p color:'green'>OK</p>")
        else:
            self.lbStatusComunicacao.setText("<p color:'red'>Falha</p>")

        if result[1]:
            self.lbStatusAuxSupply.setText("<p color:'green'>OK</p>")
        else:
            self.lbStatusAuxSupply.setText("<p color:'red'>Falha</p>")

    @pyqtSlot()
    def _start_test_sequence(self):
        self._test_thread.test_complete.connect(self._test_finished)
        self.test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass

    @pyqtSlot(dict)
    def _test_finished(self, test_result):
        self._log.test_result   = test_result['result']
        self._log.iload0        = test_result['iload'][0]
        self._log.iload1        = test_result['iload'][1]
        self._log.iload2        = test_result['iload'][2]
        self._log.iload3        = test_result['iload'][3]
        self._log.iload4        = test_result['iload'][4]
        self._log.iload5        = test_result['iload'][5]
        self._log.iload6        = test_result['iload'][6]
        self._log.iload7        = test_result['iload'][7]
        self._log.iload8        = test_result['iload'][8]
        self._log.iload9        = test_result['iload'][9]
        self._log.iload10       = test_result['iload'][10]
        self.lbTestStatus.setText("Teste Finalizado!")
        self.lbTestResult.setText(self._log.test_result)

    @pyqtSlot(dict, dict)
    def _treat_server_response(self, device_res, log_res):
        res_key = 'StatusCode'
        err_key = 'error'
        if res_key in device_res.keys() and res_key in log_res.keys():
            if device_res[res_key] == '200' and log_res[res_key] == '200':
                self.lbStatusSubmitRequest.setText('Sucesso!!!')
                self.lbRespDevice.setText(device_res['Message'])
                self.lbRespLog.setText(log_res['Message'])
            else:
                self.lbStatusSubmitRequest.setText('Falha!!!')
                self.lbRespDevice.setText(device_res['Message'])
                self.lbRespLog.setText(log_res['Message'])
        elif err_key in device_res.keys() or err_key in log_res.keys():
            self.lbStatusSubmitRequest.setText('Falha!!!')
            self.lbRespDevice.setText(str(device_res))
            self.lbRespLog.setText(str(log_res))

        self._web_request_status = True

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DCCTWindow()
    gui.show()
    sys.exit(app.exec_())

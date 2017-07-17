#!/usr/bin/python3
import sys
import glob
import serial
import simplejson as json
from PyQt5.uic import loadUiType
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage, QMessageBox
from dccttest import DCCTTest
#from dmreader import *
from dcctdata import *
from webrequest import *

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class PowerModuleWindow(QWizard, Ui_Class):

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 115200
        self._serial_numbers = [None for i in range(4)]

        self._power_module = []
        self._log = []

        self._list_serial_ports()
        self._serial_port_status = False
        self._web_request_status = False

        self._test_thread = PowerModuleTest()
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
        self.leSerialNumber0.setReadOnly(True)
        self.leSerialNumber0.clear()
        self.leSerialNumber1.setReadOnly(True)
        self.leSerialNumber1.clear()
        self.leSerialNumber2.setReadOnly(True)
        self.leSerialNumber2.clear()
        self.leSerialNumber3.setReadOnly(True)
        self.leSerialNumber3.clear()
        self.cbEnableSerialNumberEdit0.setChecked(False)
        self.cbEnableSerialNumberEdit1.setChecked(False)
        self.cbEnableSerialNumberEdit2.setChecked(False)
        self.cbEnableSerialNumberEdit3.setChecked(False)
        self.cbDisableModuleReadSerial0.setChecked(False)
        self.cbDisableModuleReadSerial1.setChecked(False)
        self.cbDisableModuleReadSerial2.setChecked(False)
        self.cbDisableModuleReadSerial3.setChecked(False)
        self.lbStatusComunicacao.setText("...")
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult.setText("Aguarde...")
        self.teTestReport.clear()
        self.lbStatusSubmitRequest.setText("Aguarde...")

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbReadSerialNumber0.clicked.connect(self._read_serial_number_0)
        self.pbReadSerialNumber1.clicked.connect(self._read_serial_number_1)
        self.pbReadSerialNumber2.clicked.connect(self._read_serial_number_2)
        self.pbReadSerialNumber3.clicked.connect(self._read_serial_number_3)
        self.cbEnableSerialNumberEdit0.stateChanged.connect(self._treat_read_serial_edit_0)
        self.cbEnableSerialNumberEdit1.stateChanged.connect(self._treat_read_serial_edit_1)
        self.cbEnableSerialNumberEdit2.stateChanged.connect(self._treat_read_serial_edit_2)
        self.cbEnableSerialNumberEdit3.stateChanged.connect(self._treat_read_serial_edit_3)
        self.cbDisableModuleReadSerial0.stateChanged.connect(self._disbl_read_serial_edit_0)
        self.cbDisableModuleReadSerial1.stateChanged.connect(self._disbl_read_serial_edit_1)
        self.cbDisableModuleReadSerial2.stateChanged.connect(self._disbl_read_serial_edit_2)
        self.cbDisableModuleReadSerial3.stateChanged.connect(self._disbl_read_serial_edit_3)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        self.pbCommunicationTest.clicked.connect(self._communication_test)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageIntro.setButtonText(self.NextButton, "Próximo")
        self.PageIntro.setButtonText(self.BackButton, "Anterior")
        self.PageIntro.setButtonText(self.CancelButton, "Cancelar")

        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectModule.setButtonText(self.NextButton, "Próximo")
        self.PageConnectModule.setButtonText(self.BackButton, "Anterior")
        self.PageConnectModule.setButtonText(self.CancelButton, "Cancelar")

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

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_module(self):
        pass

    def _initialize_page_test_serial_port(self):
        pass

    def _initialize_page_start_test(self):
        pass

    def _initialize_page_submit_report(self):
        self._web_request.device = self._power_module
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
        validate = False

        try:
            self._serial_numbers[0] = int(self.leSerialNumber0.text())
            validate = True
        except ValueError:
            pass

        try:
            self._serial_numbers[1] = int(self.leSerialNumber1.text())
            validate = True
        except ValueError:
            pass

        try:
            self._serial_numbers[2] = int(self.leSerialNumber2.text())
            validate = True
        except ValueError:
            pass

        try:
            self._serial_numbers[3] = int(self.leSerialNumber3.text())
            validate = True
        except ValueError:
            pass

        if validate:
            self._treat_serial_number_data(serial)
        return validate

    def _validate_page_connect_module(self):
        return True

    def _validate_page_test_serial_port(self):
        return True

    def _validate_page_start_test(self):
        print('Validate Start Test')
        return True

    def _validate_page_submit_report(self):
        print('Validate Submit')
        self._initialize_widgets()
        self._serial_numbers = [None for i in range(4)]
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
            self._initialize_page_connect_module()
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
            return self._validate_page_connect_module()

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
    def _read_serial_number_0(self):
        data = self._read_serial_number()
        if data is not None:
            self._serial_numbers[0] = data
        self.leSerialNumber0.setText(str(data))

    @pyqtSlot()
    def _read_serial_number_1(self):
        data = self._read_serial_number()
        if data is not None:
            self._serial_numbers[1] = data
            self.leSerialNumber1.setText(str(data))

    @pyqtSlot()
    def _read_serial_number_2(self):
        data = self._read_serial_number()
        if data is not None:
            self._serial_numbers[2] = data
            self.leSerialNumber2.setText(str(data))

    @pyqtSlot()
    def _read_serial_number_3(self):
        data = self._read_serial_number()
        if data is not None:
            self._serial_numbers[3] = data
            self.leSerialNumber3.setText(str(data))

    @pyqtSlot()
    def _treat_read_serial_edit_0(self):
        if self.cbEnableSerialNumberEdit0.isChecked():
            self.leSerialNumber0.setReadOnly(False)
        else:
            self.leSerialNumber0.setReadOnly(True)

    @pyqtSlot()
    def _treat_read_serial_edit_1(self):
        if self.cbEnableSerialNumberEdit1.isChecked():
            self.leSerialNumber1.setReadOnly(False)
        else:
            self.leSerialNumber1.setReadOnly(True)

    @pyqtSlot()
    def _treat_read_serial_edit_2(self):
        if self.cbEnableSerialNumberEdit2.isChecked():
            self.leSerialNumber2.setReadOnly(False)
        else:
            self.leSerialNumber2.setReadOnly(True)

    @pyqtSlot()
    def _treat_read_serial_edit_3(self):
        if self.cbEnableSerialNumberEdit3.isChecked():
            self.leSerialNumber3.setReadOnly(False)
        else:
            self.leSerialNumber3.setReadOnly(True)

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

    @pyqtSlot(list)
    def _test_finished(self, test_result):
        for item in test_result:
            log = PowerModuleLog()
            log.test_result   = item['result']
            log.iload0        = item['iload'][0]
            log.iload1        = item['iload'][1]
            log.iload2        = item['iload'][2]
            log.iload3        = item['iload'][3]
            log.iload4        = item['iload'][4]
            log.iload5        = item['iload'][5]
            log.vload0        = item['vload'][0]
            log.vload1        = item['vload'][1]
            log.vload2        = item['vload'][2]
            log.vload3        = item['vload'][3]
            log.vload4        = item['vload'][4]
            log.vload5        = item['vload'][5]
            log.vdclink0      = item['vdclink'][0]
            log.vdclink1      = item['vdclink'][1]
            log.vdclink2      = item['vdclink'][2]
            log.vdclink3      = item['vdclink'][3]
            log.vdclink4      = item['vdclink'][4]
            log.vdclink5      = item['vdclink'][5]
            log.temperatura0  = item['temperatura'][0]
            log.temperatura1  = item['temperatura'][1]
            log.temperatura2  = item['temperatura'][2]
            log.temperatura3  = item['temperatura'][3]
            log.temperatura4  = item['temperatura'][4]
            log.temperatura5  = item['temperatura'][5]
            self._log.append(log)
        self.lbTestStatus.setText("Teste Finalizado!")
        self.lbTestResult.setText(self._log.test_result)

    @pyqtSlot(dict, dict)
    def _treat_server_response(self, device_res, log_res):
        res_key = 'SucessCode'
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

    """*************************************************
    ***************** System Methods *******************
    *************************************************"""
    def _treat_serial_number_data(self, serial):
        for item in serial:
            if item is not None:
                power_module = PowerModule()
                power_module.serial_number = item
                self._power_module.append(power_module)

    def _read_serial_number(self):
        data = ReadDataMatrix()
        if data == None:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("Erro de Leitura")
            msfg.setInformativeText("Pressione ESC e tente novamente \
                                    ou insira manualmente")
            msg.setWindowTitle("Erro de Leitura")
            msg._exec()
        else:
            return data

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PowerModuleWindow()
    gui.show()
    sys.exit(app.exec_())

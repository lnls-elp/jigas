#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmscanner import Scanner
from PyQt5.uic import loadUiType
from hradccalib import HRADCCalib
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class HRADCWindow(QWizard, Ui_Class):

    # Page numbers
    (num_intro_page, num_serial_number, num_connect_hradc,
    num_serial_port, num_start_test) = range(5)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 6000000

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False

        self._test_thread = HRADCCalib()

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
        self.leDmCode0.clear()
        self.leDmCode1.clear()
        self.leDmCode2.clear()
        self.leDmCode3.clear()
        self.leSerialNumber0.setReadOnly(True)
        self.leSerialNumber0.clear()
        self.leSerialNumber1.setReadOnly(True)
        self.leSerialNumber1.clear()
        self.leSerialNumber2.setReadOnly(True)
        self.leSerialNumber2.clear()
        self.leSerialNumber3.setReadOnly(True)
        self.leSerialNumber3.clear()
        self.leMaterialCode0.setReadOnly(True)
        self.leMaterialCode0.clear()
        self.leMaterialCode1.setReadOnly(True)
        self.leMaterialCode1.clear()
        self.leMaterialCode2.setReadOnly(True)
        self.leMaterialCode2.clear()
        self.leMaterialCode3.setReadOnly(True)
        self.leMaterialCode3.clear()
        self.leMaterialName0.setReadOnly(True)
        self.leMaterialName0.clear()
        self.leMaterialName1.setReadOnly(True)
        self.leMaterialName1.clear()
        self.leMaterialName2.setReadOnly(True)
        self.leMaterialName2.clear()
        self.leMaterialName3.setReadOnly(True)
        self.leMaterialName3.clear()
        self.cbDisableModuleReadSerial0.setChecked(False)
        self.cbDisableModuleReadSerial1.setChecked(False)
        self.cbDisableModuleReadSerial2.setChecked(False)
        self.cbDisableModuleReadSerial3.setChecked(False)
        self.lbStatusComunicacao.setText("...")
        self.lbTestStatus.setText("Clique para Iniciar Calibração")
        self.lbTestResult.setText("Aguarde...")
        self.teTestReport.clear()

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.cbDisableModuleReadSerial0.stateChanged.connect(self._disbl_read_serial_edit_0)
        self.cbDisableModuleReadSerial1.stateChanged.connect(self._disbl_read_serial_edit_1)
        self.cbDisableModuleReadSerial2.stateChanged.connect(self._disbl_read_serial_edit_2)
        self.cbDisableModuleReadSerial3.stateChanged.connect(self._disbl_read_serial_edit_3)
        self.leDmCode0.editingFinished.connect(self._treat_dmcode0)
        self.leDmCode1.editingFinished.connect(self._treat_dmcode1)
        self.leDmCode2.editingFinished.connect(self._treat_dmcode2)
        self.leDmCode3.editingFinished.connect(self._treat_dmcode3)
        self.pbStartCalib.clicked.connect(self._start_calib_sequence)
        self.pbCommunicationTest.clicked.connect(self._communication_test)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageIntro.setButtonText(self.NextButton, "Próximo")
        self.PageIntro.setButtonText(self.BackButton, "Anterior")
        self.PageIntro.setButtonText(self.CancelButton, "Cancelar")

        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectHradc.setButtonText(self.NextButton, "Próximo")
        self.PageConnectHradc.setButtonText(self.BackButton, "Anterior")
        self.PageConnectHradc.setButtonText(self.CancelButton, "Cancelar")

        self.PageTestSerialPort.setButtonText(self.NextButton, "Próximo")
        self.PageTestSerialPort.setButtonText(self.BackButton, "Anterior")
        self.PageTestSerialPort.setButtonText(self.CancelButton, "Cancelar")

        self.PageStartTest.setButtonText(self.NextButton, "Novo Teste")
        self.PageStartTest.setButtonText(self.BackButton, "Anterior")
        self.PageStartTest.setButtonText(self.CancelButton, "Cancelar")

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

    def _restart_test_thread(self):
        self._test_thread.calib_complete.disconnect()
        self._test_thread.update_gui.disconnect()
        self._test_thread.quit()
        self._test_thread.wait()

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_hradc(self):
        pass

    def _initialize_page_test_serial_port(self):
        pass

    def _initialize_page_start_test(self):
        self.teTestReport.clear()

    """*************************************************
    ************** Pages Validation ********************
    *************************************************"""
    def _validate_intro_page(self):
        if self._serial_port_status:
            return True
        return False

    def _validate_page_serial_number(self):
        try:
            self._test_thread.serial_mod0 = int(self.leSerialNumber0.text())
        except ValueError:
            self._test_thread.serial_mod0 = None
            if not self.cbDisableModuleReadSerial0.isChecked():
                return False

        try:
            self._test_thread.serial_mod1 = int(self.leSerialNumber1.text())
        except ValueError:
            self._test_thread.serial_mod1 = None
            if not self.cbDisableModuleReadSerial1.isChecked():
                return False

        try:
            self._test_thread.serial_mod2 = int(self.leSerialNumber2.text())
        except ValueError:
            self._test_thread.serial_mod2 = None
            if not self.cbDisableModuleReadSerial2.isChecked():
                return False

        try:
            self._test_thread.serial_mod3 = int(self.leSerialNumber3.text())
        except ValueError:
            self._test_thread.serial_mod3 = None
            if not self.cbDisableModuleReadSerial3.isChecked():
                return False

        if self.cbDisableModuleReadSerial0.isChecked() and \
            self.cbDisableModuleReadSerial1.isChecked() and \
            self.cbDisableModuleReadSerial2.isChecked() and \
            self.cbDisableModuleReadSerial3.isChecked():
            return False

        return True

    def _validate_page_connect_hradc(self):
        return True

    def _validate_page_test_serial_port(self):
        return self._test_serial_port_status

    def _validate_page_start_test(self):
        self._initialize_widgets()
        self._restart_variables()
        self._restart_test_thread()
        while self.currentId() is not self.num_serial_number:
            self.back()
        return False

    """*************************************************
    *********** Default Methods (Wizard) ***************
    *************************************************"""
    def initializePage(self, page):
        if page == self.num_intro_page:
            self._initialize_intro_page()

        elif page == self.num_serial_number:
            self._initialize_page_serial_number()

        elif page == self.num_connect_hradc:
            self._initialize_page_connect_hradc()

        elif page == self.num_serial_port:
            self._initialize_page_test_serial_port()

        elif page == self.num_start_test:
            self._initialize_page_start_test()

        else:
            pass

    def validateCurrentPage(self):
        current_id = self.currentId()
        if current_id == self.num_intro_page:
            return self._validate_intro_page()

        elif current_id == self.num_serial_number:
            return self._validate_page_serial_number()

        elif current_id == self.num_connect_hradc:
            return self._validate_page_connect_hradc()

        elif current_id == self.num_serial_port:
            return self._validate_page_test_serial_port()

        elif current_id == self.num_start_test:
            return self._validate_page_start_test()

        else:
            return True


    """*************************************************
    ******************* PyQt Slots *********************
    *************************************************"""

    @pyqtSlot()
    def _treat_dmcode0(self):
        code = self.leDmCode0.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber0.setText(data['serial'])
            self.leMaterialCode0.setText(data['material'])
            self.leMaterialName0.setText(scan.get_material_name(data['material']))
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber0.clear()
            self.leMaterialCode0.clear()
            self.leMaterialName0.clear()


    @pyqtSlot()
    def _treat_dmcode1(self):
        code = self.leDmCode1.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber1.setText(data['serial'])
            self.leMaterialCode1.setText(data['material'])
            self.leMaterialName1.setText(scan.get_material_name(data['material']))
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber1.clear()
            self.leMaterialCode1.clear()
            self.leMaterialName1.clear()

    @pyqtSlot()
    def _treat_dmcode2(self):
        code = self.leDmCode2.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber2.setText(data['serial'])
            self.leMaterialCode2.setText(data['material'])
            self.leMaterialName2.setText(scan.get_material_name(data['material']))
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber2.clear()
            self.leMaterialCode2.clear()
            self.leMaterialName2.clear()

    @pyqtSlot()
    def _treat_dmcode3(self):
        code = self.leDmCode3.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber3.setText(data['serial'])
            self.leMaterialCode3.setText(data['material'])
            self.leMaterialName3.setText(scan.get_material_name(data['material']))
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber3.clear()
            self.leMaterialCode3.clear()
            self.leMaterialName3.clear()


    @pyqtSlot()
    def _disbl_read_serial_edit_0(self):
        if self.cbDisableModuleReadSerial0.isChecked():
            self.leSerialNumber0.clear()
            self.leSerialNumber0.setEnabled(False)
            self.leMaterialCode0.setEnabled(False)
            self.leMaterialName0.setEnabled(False)
        else:
            self.leSerialNumber0.setEnabled(True)
            self.leMaterialCode0.setEnabled(True)
            self.leMaterialName0.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_1(self):
        if self.cbDisableModuleReadSerial1.isChecked():
            self.leSerialNumber1.clear()
            self.leSerialNumber1.setEnabled(False)
            self.leMaterialCode1.setEnabled(False)
            self.leMaterialName1.setEnabled(False)
        else:
            self.leSerialNumber1.setEnabled(True)
            self.leMaterialCode1.setEnabled(True)
            self.leMaterialName1.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_2(self):
        if self.cbDisableModuleReadSerial2.isChecked():
            self.leSerialNumber2.clear()
            self.leSerialNumber2.setEnabled(False)
            self.leMaterialCode2.setEnabled(False)
            self.leMaterialName2.setEnabled(False)
        else:
            self.leSerialNumber2.setEnabled(True)
            self.leMaterialCode2.setEnabled(True)
            self.leMaterialName2.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_3(self):
        if self.cbDisableModuleReadSerial3.isChecked():
            self.leSerialNumber3.clear()
            self.leSerialNumber3.setEnabled(False)s
            self.leMaterialCode3.setEnabled(False)
            self.leMaterialName3.setEnabled(False)
        else:
            self.leSerialNumber3.setEnabled(True)
            self.leMaterialCode3.setEnabled(True)
            self.leMaterialName3.setEnabled(True)

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
    def _start_calib_sequence(self):
        self._test_thread.calib_complete.connect(self._calib_finished)
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass

    @pyqtSlot(bool)
    def _calib_finished(self, result):
        if result:
            self.lbTestResult.setText("Sucesso")
        else:
            self.lbTestResult.setText("Erro")

    @pyqtSlot(str)
    def _update_test_log(self, value):
        self.teTestReport.append(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HRADCWindow()
    gui.show()
    sys.exit(app.exec_())

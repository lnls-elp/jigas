#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmscanner import Scanner
from burnintest import BurnInTest
from PyQt5.uic import loadUiType
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class PowerSupplyWindow(QWizard, Ui_Class):

    # Page numbers
    (num_intro_page, num_serial_number, num_address_instr,
    num_addressing, num_power_fbp, num_start_test) = range(6)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 6000000

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False

        self._serial_number = []

        self._test_thread = BurnInTest()

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
        self.leDmCode4.clear()
        self.leDmCode5.clear()
        self.leDmCode6.clear()
        self.leDmCode7.clear()
        self.leDmCode8.clear()
        self.leDmCode9.clear()
        self.leSerialNumber0.setReadOnly(True)
        self.leSerialNumber0.clear()
        self.leSerialNumber1.setReadOnly(True)
        self.leSerialNumber1.clear()
        self.leSerialNumber2.setReadOnly(True)
        self.leSerialNumber2.clear()
        self.leSerialNumber3.setReadOnly(True)
        self.leSerialNumber3.clear()
        self.leSerialNumber4.setReadOnly(True)
        self.leSerialNumber4.clear()
        self.leSerialNumber5.setReadOnly(True)
        self.leSerialNumber5.clear()
        self.leSerialNumber6.setReadOnly(True)
        self.leSerialNumber6.clear()
        self.leSerialNumber7.setReadOnly(True)
        self.leSerialNumber7.clear()
        self.leSerialNumber8.setReadOnly(True)
        self.leSerialNumber8.clear()
        self.leSerialNumber9.setReadOnly(True)
        self.leSerialNumber9.clear()
        self.leMaterialCode0.setReadOnly(True)
        self.leMaterialCode0.clear()
        self.leMaterialCode1.setReadOnly(True)
        self.leMaterialCode1.clear()
        self.leMaterialCode2.setReadOnly(True)
        self.leMaterialCode2.clear()
        self.leMaterialCode3.setReadOnly(True)
        self.leMaterialCode3.clear()
        self.leMaterialCode4.setReadOnly(True)
        self.leMaterialCode4.clear()
        self.leMaterialCode5.setReadOnly(True)
        self.leMaterialCode5.clear()
        self.leMaterialCode6.setReadOnly(True)
        self.leMaterialCode6.clear()
        self.leMaterialCode7.setReadOnly(True)
        self.leMaterialCode7.clear()
        self.leMaterialCode8.setReadOnly(True)
        self.leMaterialCode8.clear()
        self.leMaterialCode9.setReadOnly(True)
        self.leMaterialCode9.clear()
        self.cbDisableFbpSlot0.setChecked(False)
        self.cbDisableFbpSlot1.setChecked(False)
        self.cbDisableFbpSlot2.setChecked(False)
        self.cbDisableFbpSlot3.setChecked(False)
        self.cbDisableFbpSlot4.setChecked(False)
        self.cbDisableFbpSlot5.setChecked(False)
        self.cbDisableFbpSlot6.setChecked(False)
        self.cbDisableFbpSlot7.setChecked(False)
        self.cbDisableFbpSlot8.setChecked(False)
        self.cbDisableFbpSlot9.setChecked(False)
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult.setText("Aguarde...")
        self.teTestReport.clear()

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.cbDisableFbpSlot0.stateChanged.connect(self._disbl_read_serial_edit_0)
        self.cbDisableFbpSlot1.stateChanged.connect(self._disbl_read_serial_edit_1)
        self.cbDisableFbpSlot2.stateChanged.connect(self._disbl_read_serial_edit_2)
        self.cbDisableFbpSlot3.stateChanged.connect(self._disbl_read_serial_edit_3)
        self.cbDisableFbpSlot4.stateChanged.connect(self._disbl_read_serial_edit_4)
        self.cbDisableFbpSlot5.stateChanged.connect(self._disbl_read_serial_edit_5)
        self.cbDisableFbpSlot6.stateChanged.connect(self._disbl_read_serial_edit_6)
        self.cbDisableFbpSlot7.stateChanged.connect(self._disbl_read_serial_edit_7)
        self.cbDisableFbpSlot8.stateChanged.connect(self._disbl_read_serial_edit_8)
        self.cbDisableFbpSlot9.stateChanged.connect(self._disbl_read_serial_edit_9)
        self.leDmCode0.editingFinished.connect(self._treat_dmcode0)
        self.leDmCode1.editingFinished.connect(self._treat_dmcode1)
        self.leDmCode2.editingFinished.connect(self._treat_dmcode2)
        self.leDmCode3.editingFinished.connect(self._treat_dmcode3)
        self.leDmCode4.editingFinished.connect(self._treat_dmcode4)
        self.leDmCode5.editingFinished.connect(self._treat_dmcode5)
        self.leDmCode6.editingFinished.connect(self._treat_dmcode6)
        self.leDmCode7.editingFinished.connect(self._treat_dmcode7)
        self.leDmCode8.editingFinished.connect(self._treat_dmcode8)
        self.leDmCode9.editingFinished.connect(self._treat_dmcode9)
        self.pbSetAddress.clicked.connect(self._set_address)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageIntro.setButtonText(self.NextButton, "Próximo")
        self.PageIntro.setButtonText(self.BackButton, "Anterior")
        self.PageIntro.setButtonText(self.CancelButton, "Cancelar")

        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageAddressingInstructions.setButtonText(self.NextButton, "Próximo")
        self.PageAddressingInstructions.setButtonText(self.BackButton, "Anterior")
        self.PageAddressingInstructions.setButtonText(self.CancelButton, "Cancelar")

        self.PageAddressing.setButtonText(self.NextButton, "Próximo")
        self.PageAddressing.setButtonText(self.BackButton, "Anterior")
        self.PageAddressing.setButtonText(self.CancelButton, "Cancelar")

        self.PagePowerFBP.setButtonText(self.NextButton, "Próximo")
        self.PagePowerFBP.setButtonText(self.BackButton, "Anterior")
        self.PagePowerFBP.setButtonText(self.CancelButton, "Cancelar")

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
            ports = glob.glob('/dev/*')
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

    def _restart_test_thread(self):
        self._test_thread.test_complete.disconnect()
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

    def _initialize_page_addressing_instructions(self):
        pass

    def _initialize_page_addressing(self):
        pass

    def _initialize_page_power_fbp(self):
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
        serial = None

        try:
            serial = int(self.leSerialNumber0.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot0.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber1.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot1.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber2.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot2.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber3.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot3.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber4.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot4.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber5.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot5.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber6.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot6.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber7.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot7.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber8.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot8.isChecked():
                return False

        try:
            serial = int(self.leSerialNumber9.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot9.isChecked():
                return False

        if self.cbDisableFbpSlot1.isChecked() and \
            self.cbDisableFbpSlot2.isChecked() and \
            self.cbDisableFbpSlot3.isChecked() and \
            self.cbDisableFbpSlot4.isChecked() and \
            self.cbDisableFbpSlot5.isChecked() and \
            self.cbDisableFbpSlot6.isChecked() and \
            self.cbDisableFbpSlot7.isChecked() and \
            self.cbDisableFbpSlot8.isChecked() and \
            self.cbDisableFbpSlot9.isChecked() and \
            self.cbDisableFbpSlot0.isChecked():
            return False

        self._test_thread.serial_number = self._serial_number[:]

        return True


    def _validate_page_addressing_instructions(self):
        return True

    def _validate_page_addressing(self):
        return True

    def _validate_page_power_fbp(self):
        return True


    def _validate_page_start_test(self):
        print('Validate Start Test')
        self._initialize_widgets()
        self._restart_test_thread()
        del self._serial_number[:]
        while self.currentId() is not self.num_serial_number:
            self.back()
        return False


    """*************************************************
    *********** Default Methods (Wizard) ***************
    *************************************************"""
    def initializePage(self, page):
        if page == self.num_intro_page:
            self._initialize_intro_page()
            print(self.currentId())

        elif page == self.num_serial_number:
            self._initialize_page_serial_number()
            print(self.currentId())

        elif page == self.num_address_instr:
            self._initialize_page_addressing_instructions()
            print(self.currentId())

        elif page == self.num_addressing:
            self._initialize_page_addressing()
            print(self.currentId())

        elif page == self.num_power_fbp:
            self._initialize_page_power_fbp()
            print(self.currentId())

        elif page == self.num_start_test:
            self._initialize_page_start_test()
            print(self.currentId())

        else:
            pass

    def validateCurrentPage(self):
        current_id = self.currentId()
        if current_id == self.num_intro_page:
            return self._validate_intro_page()

        elif current_id == self.num_serial_number:
            return self._validate_page_serial_number()

        elif current_id == self.num_address_instr:
            return self._validate_page_addressing_instructions()

        elif current_id == self.num_addressing:
            return self._validate_page_addressing()

        elif current_id == self.num_power_fbp:
            return self._validate_page_power_fbp()

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
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber0.clear()
            self.leMaterialCode0.clear()


    @pyqtSlot()
    def _treat_dmcode1(self):
        code = self.leDmCode1.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber1.setText(data['serial'])
            self.leMaterialCode1.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber1.clear()
            self.leMaterialCode1.clear()

    @pyqtSlot()
    def _treat_dmcode2(self):
        code = self.leDmCode2.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber2.setText(data['serial'])
            self.leMaterialCode2.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber2.clear()
            self.leMaterialCode2.clear()

    @pyqtSlot()
    def _treat_dmcode3(self):
        code = self.leDmCode3.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber3.setText(data['serial'])
            self.leMaterialCode3.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber3.clear()
            self.leMaterialCode3.clear()

    @pyqtSlot()
    def _treat_dmcode4(self):
        code = self.leDmCode4.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber4.setText(data['serial'])
            self.leMaterialCode4.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber4.clear()
            self.leMaterialCode4.clear()


    @pyqtSlot()
    def _treat_dmcode5(self):
        code = self.leDmCode5.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber5.setText(data['serial'])
            self.leMaterialCode5.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber5.clear()
            self.leMaterialCode5.clear()

    @pyqtSlot()
    def _treat_dmcode6(self):
        code = self.leDmCode6.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber6.setText(data['serial'])
            self.leMaterialCode6.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber6.clear()
            self.leMaterialCode6.clear()

    @pyqtSlot()
    def _treat_dmcode7(self):
        code = self.leDmCode7.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber7.setText(data['serial'])
            self.leMaterialCode7.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber7.clear()
            self.leMaterialCode7.clear()

    @pyqtSlot()
    def _treat_dmcode8(self):
        code = self.leDmCode8.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber8.setText(data['serial'])
            self.leMaterialCode8.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber8.clear()
            self.leMaterialCode8.clear()

    @pyqtSlot()
    def _treat_dmcode9(self):
        code = self.leDmCode9.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber9.setText(data['serial'])
            self.leMaterialCode9.setText(data['material'])
        else:
            self.leDmCode0.setText("Codigo Invalido!")
            self.leSerialNumber9.clear()
            self.leMaterialCode9.clear()

    @pyqtSlot()
    def _disbl_read_serial_edit_0(self):
        if self.cbDisableModuleReadSerial0.isChecked():
            self.leSerialNumber0.clear()
            self.leSerialNumber0.setEnabled(False)
            self.leMaterialCode0.setEnabled(False)
            self.leDmCode0.setEnabled(False)
        else:
            self.leSerialNumber0.setEnabled(True)
            self.leMaterialCode0.setEnabled(True)
            self.leDmCode0.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_1(self):
        if self.cbDisableModuleReadSerial1.isChecked():
            self.leSerialNumber1.clear()
            self.leSerialNumber1.setEnabled(False)
            self.leMaterialCode1.setEnabled(False)
            self.leDmCode1.setEnabled(False)
        else:
            self.leSerialNumber1.setEnabled(True)
            self.leMaterialCode1.setEnabled(True)
            self.leDmCode1.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_2(self):
        if self.cbDisableModuleReadSerial2.isChecked():
            self.leSerialNumber2.clear()
            self.leSerialNumber2.setEnabled(False)
            self.leMaterialCode2.setEnabled(False)
            self.leDmCode2.setEnabled(False)
        else:
            self.leSerialNumber2.setEnabled(True)
            self.leMaterialCode2.setEnabled(True)
            self.leDmCode2.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_3(self):
        if self.cbDisableModuleReadSerial3.isChecked():
            self.leSerialNumber3.clear()
            self.leSerialNumber3.setEnabled(False)
            self.leMaterialCode3.setEnabled(False)
            self.leDmCode3.setEnabled(False)
        else:
            self.leSerialNumber3.setEnabled(True)
            self.leMaterialCode3.setEnabled(True)
            self.leDmCode3.setEnabled(True)


    @pyqtSlot()
    def _disbl_read_serial_edit_4(self):
        if self.cbDisableModuleReadSerial4.isChecked():
            self.leSerialNumber4.clear()
            self.leSerialNumber4.setEnabled(False)
            self.leMaterialCode4.setEnabled(False)
            self.leDmCode4.setEnabled(False)
        else:
            self.leSerialNumber4.setEnabled(True)
            self.leMaterialCode4.setEnabled(True)
            self.leDmCode4.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_5(self):
        if self.cbDisableModuleReadSerial5.isChecked():
            self.leSerialNumber5.clear()
            self.leSerialNumber5.setEnabled(False)
            self.leMaterialCode5.setEnabled(False)
            self.leDmCode5.setEnabled(False)
        else:
            self.leSerialNumber5.setEnabled(True)
            self.leMaterialCode5.setEnabled(True)
            self.leDmCode5.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_6(self):
        if self.cbDisableModuleReadSerial6.isChecked():
            self.leSerialNumber6.clear()
            self.leSerialNumber6.setEnabled(False)
            self.leMaterialCode6.setEnabled(False)
            self.leDmCode6.setEnabled(False)
        else:
            self.leSerialNumber6.setEnabled(True)
            self.leMaterialCode6.setEnabled(True)
            self.leDmCode6.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_7(self):
        if self.cbDisableModuleReadSerial7.isChecked():
            self.leSerialNumber7.clear()
            self.leSerialNumber7.setEnabled(False)
            self.leMaterialCode7.setEnabled(False)
            self.leDmCode7.setEnabled(False)
        else:
            self.leSerialNumber7.setEnabled(True)
            self.leMaterialCode7.setEnabled(True)
            self.leDmCode7.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_8(self):
        if self.cbDisableModuleReadSerial8.isChecked():
            self.leSerialNumber8.clear()
            self.leSerialNumber8.setEnabled(False)
            self.leMaterialCode8.setEnabled(False)
            self.leDmCode8.setEnabled(False)
        else:
            self.leSerialNumber8.setEnabled(True)
            self.leMaterialCode8.setEnabled(True)
            self.leDmCode8.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_edit_9(self):
        if self.cbDisableModuleReadSerial9.isChecked():
            self.leSerialNumber9.clear()
            self.leSerialNumber9.setEnabled(False)
            self.leMaterialCode9.setEnabled(False)
            self.leDmCode9.setEnabled(False)
        else:
            self.leSerialNumber9.setEnabled(True)
            self.leMaterialCode9.setEnabled(True)
            self.leDmCode9.setEnabled(True)


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
    def _set_address(self):
        write_gui = self._test_thread.set_address()
        self.lbAddress.setText(write_gui[0])
        self.teAddressingLog.setText(write_gui[1])
        #pass

    @pyqtSlot()
    def _start_test_sequence(self):
        self._test_thread.test_complete.connect(self._test_finished)
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass

    @pyqtSlot(bool)
    def _test_finished(self, result):
        if result:
            self.lbTestResult.setText("Aprovado")
        else:
            self.lbTestResult.setText("Reprovado")

    @pyqtSlot(str)
    def _update_test_log(self, value):
        self.teTestReport.append(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = PowerSupplyWindow()
    gui.show()
    sys.exit(app.exec_())

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
        self.leSerialNumber1.clear()
        self.leSerialNumber2.clear()
        self.leSerialNumber3.clear()
        self.leSerialNumber4.clear()
        self.leSerialNumber5.clear()
        self.leSerialNumber6.clear()
        self.leSerialNumber7.clear()
        self.leSerialNumber8.clear()
        self.leSerialNumber9.clear()
        self.leSerialNumber10.clear()
        self.cbDisableFbpSlot1.setChecked(False)
        self.cbDisableFbpSlot2.setChecked(False)
        self.cbDisableFbpSlot3.setChecked(False)
        self.cbDisableFbpSlot4.setChecked(False)
        self.cbDisableFbpSlot5.setChecked(False)
        self.cbDisableFbpSlot6.setChecked(False)
        self.cbDisableFbpSlot7.setChecked(False)
        self.cbDisableFbpSlot8.setChecked(False)
        self.cbDisableFbpSlot9.setChecked(False)
        self.cbDisableFbpSlot10.setChecked(False)
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult.setText("Aguarde...")
        self.teTestReport.clear()

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbReadSerialNumber1.clicked.connect(self._read_serial_number_1)
        self.pbReadSerialNumber2.clicked.connect(self._read_serial_number_2)
        self.pbReadSerialNumber3.clicked.connect(self._read_serial_number_3)
        self.pbReadSerialNumber4.clicked.connect(self._read_serial_number_4)
        self.pbReadSerialNumber5.clicked.connect(self._read_serial_number_5)
        self.pbReadSerialNumber6.clicked.connect(self._read_serial_number_6)
        self.pbReadSerialNumber7.clicked.connect(self._read_serial_number_7)
        self.pbReadSerialNumber8.clicked.connect(self._read_serial_number_8)
        self.pbReadSerialNumber9.clicked.connect(self._read_serial_number_9)
        self.pbReadSerialNumber10.clicked.connect(self._read_serial_number_10)
        self.cbDisableFbpSlot1.stateChanged.connect(self._disbl_read_serial_slot_1)
        self.cbDisableFbpSlot2.stateChanged.connect(self._disbl_read_serial_slot_2)
        self.cbDisableFbpSlot3.stateChanged.connect(self._disbl_read_serial_slot_3)
        self.cbDisableFbpSlot4.stateChanged.connect(self._disbl_read_serial_slot_4)
        self.cbDisableFbpSlot5.stateChanged.connect(self._disbl_read_serial_slot_5)
        self.cbDisableFbpSlot6.stateChanged.connect(self._disbl_read_serial_slot_6)
        self.cbDisableFbpSlot7.stateChanged.connect(self._disbl_read_serial_slot_7)
        self.cbDisableFbpSlot8.stateChanged.connect(self._disbl_read_serial_slot_8)
        self.cbDisableFbpSlot9.stateChanged.connect(self._disbl_read_serial_slot_9)
        self.cbDisableFbpSlot10.stateChanged.connect(self._disbl_read_serial_slot_10)
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

        try:
            serial = int(self.leSerialNumber10.text())
            if serial not in self._serial_number:
                self._serial_number.append(serial)
        except ValueError:
            if not self.cbDisableFbpSlot10.isChecked():
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
            self.cbDisableFbpSlot10.isChecked():
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
    def _read_serial_number_1(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber1.setText(data['serial'])


    @pyqtSlot()
    def _read_serial_number_2(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber2.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_3(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber3.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_4(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber4.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_5(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber5.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_6(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber6.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_7(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber7.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_8(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber8.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_9(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber9.setText(data['serial'])

    @pyqtSlot()
    def _read_serial_number_10(self):
        scanner = Scanner()
        data = scanner.read()
        if data is not None:
            self.leSerialNumber10.setText(data['serial'])

    @pyqtSlot()
    def _disbl_read_serial_slot_1(self):
        if self.cbDisableFbpSlot1.isChecked():
            self.leSerialNumber1.clear()
            self.leSerialNumber1.setEnabled(False)
            self.pbReadSerialNumber1.setEnabled(False)
        else:
            self.leSerialNumber1.setEnabled(True)
            self.pbReadSerialNumber1.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_2(self):
        if self.cbDisableFbpSlot2.isChecked():
            self.leSerialNumber2.clear()
            self.leSerialNumber2.setEnabled(False)
            self.pbReadSerialNumber2.setEnabled(False)
        else:
            self.leSerialNumber2.setEnabled(True)
            self.pbReadSerialNumber2.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_3(self):
        if self.cbDisableFbpSlot3.isChecked():
            self.leSerialNumber3.clear()
            self.leSerialNumber3.setEnabled(False)
            self.pbReadSerialNumber3.setEnabled(False)
        else:
            self.leSerialNumber3.setEnabled(True)
            self.pbReadSerialNumber3.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_4(self):
        if self.cbDisableFbpSlot4.isChecked():
            self.leSerialNumber4.clear()
            self.leSerialNumber4.setEnabled(False)
            self.pbReadSerialNumber4.setEnabled(False)
        else:
            self.leSerialNumber4.setEnabled(True)
            self.pbReadSerialNumber4.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_5(self):
        if self.cbDisableFbpSlot5.isChecked():
            self.leSerialNumber5.clear()
            self.leSerialNumber5.setEnabled(False)
            self.pbReadSerialNumber5.setEnabled(False)
        else:
            self.leSerialNumber5.setEnabled(True)
            self.pbReadSerialNumber5.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_6(self):
        if self.cbDisableFbpSlot6.isChecked():
            self.leSerialNumber6.clear()
            self.leSerialNumber6.setEnabled(False)
            self.pbReadSerialNumber6.setEnabled(False)
        else:
            self.leSerialNumber6.setEnabled(True)
            self.pbReadSerialNumber6.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_7(self):
        if self.cbDisableFbpSlot7.isChecked():
            self.leSerialNumber7.clear()
            self.leSerialNumber7.setEnabled(False)
            self.pbReadSerialNumber7.setEnabled(False)
        else:
            self.leSerialNumber7.setEnabled(True)
            self.pbReadSerialNumber7.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_8(self):
        if self.cbDisableFbpSlot8.isChecked():
            self.leSerialNumber8.clear()
            self.leSerialNumber8.setEnabled(False)
            self.pbReadSerialNumber8.setEnabled(False)
        else:
            self.leSerialNumber8.setEnabled(True)
            self.pbReadSerialNumber8.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_9(self):
        if self.cbDisableFbpSlot9.isChecked():
            self.leSerialNumber9.clear()
            self.leSerialNumber9.setEnabled(False)
            self.pbReadSerialNumber9.setEnabled(False)
        else:
            self.leSerialNumber9.setEnabled(True)
            self.pbReadSerialNumber9.setEnabled(True)

    @pyqtSlot()
    def _disbl_read_serial_slot_10(self):
        if self.cbDisableFbpSlot10.isChecked():
            self.leSerialNumber10.clear()
            self.leSerialNumber10.setEnabled(False)
            self.pbReadSerialNumber10.setEnabled(False)
        else:
            self.leSerialNumber10.setEnabled(True)
            self.pbReadSerialNumber10.setEnabled(True)


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
        pass

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

#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmscanner import Scanner
from pstest import PowerSupplyTest
from PyQt5.uic import loadUiType
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class PowerSupplyWindow(QWizard, Ui_Class):

    # Page numbers
    (num_intro_page, num_serial_number, num_connect_ps,
    num_serial_port, num_start_test)     = range(5)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 6000000

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False

        self._test_thread = PowerSupplyTest()

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
        self.leDmCode.clear()
        self.leSerialNumber.setReadOnly(True)
        self.leSerialNumber.clear()
        self.leMaterialCode.setReadOnly(True)
        self.leMaterialCode.clear()
        self.lbStatusComunicacao.setText("...")
        self.lbStatusAuxSupply.setText("...")
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult.setText("...")
        self.teTestReport.clear()

    def _initialize_signals(self):
        """ Configure basic signals """
        self.leDmCode.editingFinished.connect(self._treat_dmcode)
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
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

        self.PageConnectPowerSupply.setButtonText(self.NextButton, "Próximo")
        self.PageConnectPowerSupply.setButtonText(self.BackButton, "Anterior")
        self.PageConnectPowerSupply.setButtonText(self.CancelButton, "Cancelar")

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

    def _initialize_page_connect_power_supply(self):
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
        if self.leDmCode.hasFocus():
            return False

        serial = self.leSerialNumber.text()
        try:
            self._test_thread.serial_number = int(serial)
            return True
        except ValueError:
            pass
        return False

    def _validate_page_connect_power_supply(self):
        return True

    def _validate_page_test_serial_port(self):
        return self._test_serial_port_status

    def _validate_page_start_test(self):
        print('Validate Start Test')
        self._initialize_widgets()
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

        elif page == self.num_connect_ps:
            self._initialize_page_connect_power_supply()

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

        elif current_id == self.num_connect_ps:
            return self._validate_page_connect_power_supply()

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
    def _treat_dmcode(self):
        code = self.leDmCode.text()
        scan = Scanner()
        data = scan.parse_code(code)
        if data is not None:
            self.leSerialNumber.setText(data['serial'])
            self.leMaterialCode.setText(data['material'])
            self.leMaterialName.setText(scan.get_material_name(data['material']))
        else:
            self.leDmCode.setText("Codigo Invalido!")
            self.leSerialNumber.clear()
            self.leMaterialCode.clear()
            self.leMaterialName.clear()

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

        if result[0] and result[1]:
            self._test_serial_port_status = True
        else:
            self._test_serial_port_status = False

    @pyqtSlot()
    def _start_test_sequence(self):
        self.pbStartTests.setEnabled(False)
        self.pbStartTests.setText("Aguarde!")
        self.lbTestResult.setText("Aguarde...")
        self.lbTestStatus.setText("Teste iniciado. Por favor, aguarde...")
        self._test_thread.test_complete.connect(self._test_finished)
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass

    @pyqtSlot(bool)
    def _test_finished(self, result):
        self.pbStartTests.setEnabled(True)
        self.lbTestStatus.setText("Teste finalizado.")
        self.pbStartTests.setText("Iniciar\nTestes")
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

#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmreader import ReadDataMatrix
from PyQt5.uic import loadUiType
from racktest import RackTest
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class RackWindow(QWizard, Ui_Class):

    # Page numbers
    (num_intro_page, num_serial_number, num_connect_rack,
    num_serial_port, num_start_test)     = range(5)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 115200

        # self._material_bastidor = {''}

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False

        self._test_thread = RackTest()

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

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbReadSerialNumber.clicked.connect(self._read_serial_number)
        self.cbEnableSerialNumberEdit.stateChanged.connect(self._treat_read_serial_edit)
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

        self.PageConnectRack.setButtonText(self.NextButton, "Próximo")
        self.PageConnectRack.setButtonText(self.BackButton, "Anterior")
        self.PageConnectRack.setButtonText(self.CancelButton, "Cancelar")

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
        self.teTestReport.clear()

    """*************************************************
    ************** Pages Validation ********************
    *************************************************"""
    def _validate_intro_page(self):
        if self._serial_port_status:
            return True
        return False

    def _validate_page_serial_number(self):
        serial = self.leSerialNumber.text()
        try:
            self._test_thread.serial_number = int(serial)
            return True
        except ValueError:
            pass
        return False

    def _validate_page_connect_rack(self):
        return True

    def _validate_page_test_serial_port(self):
        return self._test_serial_port_status

    def _validate_page_start_test(self):
        self._initialize_widgets()
        self._restart_variables()
        self._test_thread.test_complete.disconnect()
        self._test_thread.update_gui.disconnect()
        self._test_thread.quit()
        self._test_thread.wait()
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

        elif page == self.num_connect_rack:
            self._initialize_page_connect_rack()
            print(self.currentId())

        elif page == self.num_serial_port:
            self._initialize_page_test_serial_port()
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
            print("Valida 1")
            return self._validate_page_serial_number()

        elif current_id == self.num_connect_rack:
            print("Valida 2")
            return self._validate_page_connect_rack()

        elif current_id == self.num_serial_port:
            print("Valida 3")
            return self._validate_page_test_serial_port()

        elif current_id == self.num_start_test:
            print("Valida 4")
            return self._validate_page_start_test()

        else:
            return True

    def next(self):
        if self.currentId() == self.num_start_test:
            while self.currentId() != self.num_serial_number:
                self.back()

    """*************************************************
    ******************* PyQt Slots *********************
    *************************************************"""
    @pyqtSlot()
    def _read_serial_number(self):
        #data = ReadDataMatrix()
        #if data[0] in self._material_bastidor.keys():
        #    self._test_thread.variant = self._material_dcct[data[0]]
        #    self._test_thread.serial_number = int(data[1])
        #    self.leSerialNumber.setText(data[1])
        #else:
        #    self.lbReadSerialStatus.setText("<p color:'red'><b>ERRO. Digite Manualmente!</b><p/>")
        #print("Read serial number")

        data = ReadDataMatrix()
        if data is not None:
            self._test_thread.serial_number = int(data[1])
            self.leSerialNumber.setText(data[1])
        else:
            self.lbReadSerialStatus.setText("<p color:'red'><b>ERRO. Digite Manualmente!</b><p/>")

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
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        self._test_thread.quit()
        self._test_thread.wait()

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
    gui = RackWindow()
    gui.show()
    sys.exit(app.exec_())

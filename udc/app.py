#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmreader import ReadDataMatrix
from PyQt5.uic import loadUiType
from udctest import UDCTest
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class UDCWindow(QWizard, Ui_Class):

    FAIL        = "Falha"
    SUCCESS     = "OK"

    # Page numbers
    (num_intro_page, num_serial_number, num_connect_udc,
    num_visual_test, num_serial_port, num_start_test) = range(6)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 6000000

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_serial_port_status = False

        self._test_thread = UDCTest()

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
        self.rbLedsOk.setChecked(False)
        self.rbLedsNok.setChecked(False)
        self.rbBuzzerOk.setChecked(False)
        self.rbBuzzerNok.setChecked(False)
        self.lbTestStatus.setText("Iniciar...")
        self.lbTestResult.setText("Aguarde...")
        self.lbEeprom.setText("...")
        self.lbFlash.setText("...")
        self.lbRam.setText("...")
        self.lbAdc1.setText("...")
        self.lbAdc2.setText("...")
        self.lbAdc3.setText("...")
        self.lbAdc4.setText("...")
        self.lbAdc5.setText("...")
        self.lbAdc6.setText("...")
        self.lbAdc7.setText("...")
        self.lbAdc8.setText("...")
        self.lbRtcCom.setText("...")
        self.lbRtcInt.setText("...")
        self.lbSensorTempCom.setText("...")
        self.lbSensorTempTemp.setText("...")
        self.lbRs4851.setText("...")
        self.lbRs4852.setText("...")
        self.lbRs4853.setText("...")
        self.lbAlimPlanoIsolado.setText("...")
        self.lbExpansorIo.setText("...")
        self.lbEthernet.setText("...")
        self.teTestReport.clear()

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

        self.PageConnectUDC.setButtonText(self.NextButton, "Próximo")
        self.PageConnectUDC.setButtonText(self.BackButton, "Anterior")
        self.PageConnectUDC.setButtonText(self.CancelButton, "Cancelar")

        self.PageVisualTest.setButtonText(self.NextButton, "Próximo")
        self.PageVisualTest.setButtonText(self.BackButton, "Anterior")
        self.PageVisualTest.setButtonText(self.CancelButton, "Cancelar")

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

    def _connect_test_signals(self):
        self._test_thread.test_complete.connect(self._test_finished)
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.eeprom.connect(self._update_eeprom_label)
        self._test_thread.flash.connect(self._update_flash_label)
        self._test_thread.ram.connect(self._update_ram_label)
        self._test_thread.adc.connect(self._update_adc_label)
        self._test_thread.rtc_com.connect(self._update_rtc_com_label)
        self._test_thread.rtc_int.connect(self._update_rtc_int_label)
        self._test_thread.sensor_temp_com.connect(self._update_sensor_temp_com_label)
        self._test_thread.sensor_temp_val.connect(self._update_sensor_temp_val_label)
        self._test_thread.rs485.connect(self._update_rs485_label)
        self._test_thread.isol_plane.connect(self._update_isol_plane_label)
        self._test_thread.io_expander.connect(self._update_io_expander_label)
        self._test_thread.ethernet.connect(self._update_ethernet_label)

    def _disconnect_test_signals(self):
        self._test_thread.test_complete.disconnect()
        self._test_thread.update_gui.disconnect()
        self._test_thread.eeprom.disconnect()
        self._test_thread.flash.disconnect()
        self._test_thread.ram.disconnect()
        self._test_thread.adc.disconnect()
        self._test_thread.rtc_com.disconnect()
        self._test_thread.rtc_int.disconnect()
        self._test_thread.sensor_temp_com.disconnect()
        self._test_thread.sensor_temp_val.disconnect()
        self._test_thread.rs485.disconnect()
        self._test_thread.isol_plane.disconnect()
        self._test_thread.io_expander.disconnect()
        self._test_thread.ethernet.disconnect()

    def _finish_test_thread(self):
        self._disconnect_test_signals()
        self._test_thread.quit()
        self._test_thread.wait()

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
    def _initialize_intro_page(self):
        pass

    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_udc(self):
        pass

    def _initialize_page_visual_test(self):
        pass

    def _initialize_page_test_serial_port(self):
        pass

    def _initialize_page_start_test(self):
        self.teTestReport.clear()

    """*************************************************
    ************** Pages Validation ********************
    *************************************************"""
    def _validate_intro_page(self):
        #return self._serial_port_status
        return True

    def _validate_page_serial_number(self):
        serial = self.leSerialNumber.text()
        try:
            self._test_thread.serial_number = int(serial)
            return True
        except ValueError:
            pass
        return False

    def _validate_page_connect_udc(self):
        return True

    def _validate_page_visual_test(self):
        if (self.rbLedsOk.isChecked() or self.rbLedsNok.isChecked()) and \
            (self.rbBuzzerOk.isChecked() or self.rbBuzzerNok.isChecked()):

            if self.rbLedsOk.isChecked():
                self._test_thread.led = self.SUCCESS
            else:
                self._test_thread.led = self.FAIL

            if self.rbBuzzerOk.isChecked():
                self._test_thread.buzzer = self.SUCCESS
            else:
                self._test_thread.buzzer = self.FAIL

            return True

        return False

    def _validate_page_test_serial_port(self):
        return self._test_serial_port_status

    def _validate_page_start_test(self):
        print('Validate Start Test')
        self._initialize_widgets()
        self._finish_test_thread()
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

        elif page == self.num_connect_udc:
            self._initialize_page_connect_udc()
            print(self.currentId())

        elif page == self.num_visual_test:
            self._initialize_page_visual_test()

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
            return self._validate_page_serial_number()

        elif current_id == self.num_connect_udc:
            return self._validate_page_connect_udc()

        elif current_id == self.num_visual_test:
            return self._validate_page_visual_test()

        elif current_id == self.num_serial_port:
            return self._validate_page_test_serial_port()

        elif current_id == self.num_start_test:
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

        if result:
            self._test_serial_port_status = True
        else:
            self._test_serial_port_status = False

    @pyqtSlot()
    def _start_test_sequence(self):
        self._connect_test_signals()
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

    @pyqtSlot(str)
    def _update_eeprom_label(self, value):
        self.lbEeprom.setText(value)

    @pyqtSlot(str)
    def _update_flash_label(self, value):
        self.lbFlash.setText(value)

    @pyqtSlot(str)
    def _update_ram_label(self, value):
        self.lbRam.setText(value)

    @pyqtSlot(list)
    def _update_adc_label(self, value):
        self.lbAdc1.setText(value[0])
        self.lbAdc2.setText(value[1])
        self.lbAdc3.setText(value[2])
        self.lbAdc4.setText(value[3])
        self.lbAdc5.setText(value[4])
        self.lbAdc6.setText(value[5])
        self.lbAdc7.setText(value[6])
        self.lbAdc8.setText(value[7])

    @pyqtSlot(str)
    def _update_rtc_com_label(self, value):
        self.lbRtcCom.setText(value)

    @pyqtSlot(str)
    def _update_rtc_int_label(self, value):
        self.lbRtcInt.setText(value)

    @pyqtSlot(str)
    def _update_sensor_temp_com_label(self, value):
        self.lbSensorTempCom.setText(value)

    @pyqtSlot(str)
    def _update_sensor_temp_val_label(self, value):
        self.lbSensorTempTemp.setText(value)

    @pyqtSlot(list)
    def _update_rs485_label(self, value):
        self.lbRs4851.setText(value[0])
        self.lbRs4852.setText(value[1])
        self.lbRs4853.setText(value[2])

    @pyqtSlot(str)
    def _update_isol_plane_label(self, value):
        self.lbAlimPlanoIsolado.setText(value)

    @pyqtSlot(str)
    def _update_io_expander_label(self, value):
        self.lbExpansorIo.setText(value)

    @pyqtSlot(str)
    def _update_ethernet_label(self, value):
        self.lbEthernet.setText(value)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = UDCWindow()
    gui.show()
    sys.exit(app.exec_())

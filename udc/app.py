#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmscanner import Scanner
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
    (num_serial_number, num_connect_udc, num_load_test_firmware,
    num_start_test, num_load_final_firmware, num_test_finished) = range(6)

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

        #test status
        self._load_test_firmware_status = False
        self._load_final_firmware_status = False
        self._leds_status = False
        self._buzzer_status = False
        self._communication_status = False
        self._test_result = False

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
        self.lbExpansorIO1.setText("...")
        self.lbExpansorIO2.setText("...")
        self.lbEthernetInit.setText("...")
        self.lbEthernetPing.setText("...")
        self.teTestReport.clear()
        self.lbStatusLoadingTestFirmware.setText("Clique para gravar.")
        self.lbStatusLoadingFinalFirmware.setText("Clique para gravar.")
        self.pbConnectSerialPort.setText("Conectar")
        self.pbConnectSerialPort.setEnabled(True)

    def _initialize_signals(self):
        """ Configure basic signals """
        self.leDmCode.editingFinished.connect(self._treat_dmcode)
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        self.pbLoadTestFirmware.clicked.connect(self._load_test_firmware)
        self.pbLoadFinalFirmware.clicked.connect(self._load_final_firmware)
        self.finished.connect(self._finish_wizard_execution)

    def _initialize_wizard_buttons(self):
        self.PageSerialNumber.setButtonText(self.NextButton, "Próximo")
        self.PageSerialNumber.setButtonText(self.BackButton, "Anterior")
        self.PageSerialNumber.setButtonText(self.CancelButton, "Cancelar")

        self.PageConnectUDC.setButtonText(self.NextButton, "Próximo")
        self.PageConnectUDC.setButtonText(self.BackButton, "Anterior")
        self.PageConnectUDC.setButtonText(self.CancelButton, "Cancelar")

        self.PageLoadTestFirmware.setButtonText(self.NextButton, "Próximo")
        self.PageLoadTestFirmware.setButtonText(self.BackButton, "Anterior")
        self.PageLoadTestFirmware.setButtonText(self.CancelButton, "Cancelar")

        self.PageStartTest.setButtonText(self.NextButton, "Próximo")
        self.PageStartTest.setButtonText(self.BackButton, "Anterior")
        self.PageStartTest.setButtonText(self.CancelButton, "Cancelar")

        self.PageLoadFinalFirmware.setButtonText(self.NextButton, "Novo Teste")
        self.PageLoadFinalFirmware.setButtonText(self.BackButton, "Anterior")
        self.PageLoadFinalFirmware.setButtonText(self.CancelButton, "Cancelar")

        self.PageTestFinished.setButtonText(self.NextButton, "Novo Teste")
        self.PageTestFinished.setButtonText(self.BackButton, "Anterior")
        self.PageTestFinished.setButtonText(self.CancelButton, "Cancelar")


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

    def _restart_variables(self):
        self._load_test_firmware_status = False
        self._load_final_firmware_status = False
        self._leds_status = False
        self._buzzer_status = False
        self._communication_status = False

    def _restart_test_thread(self):
        self._test_thread.test_complete.disconnect()
        self._test_thread.update_gui.disconnect()
        self._test_thread.quit()
        self._test_thread.wait()

    def _jump_to(self, value):
        if value > self.currentId():
            while self.currentId() is not value:
                self.next()

        if value < self.currentId():
            while self.currentId() is not value:
                self.back()

    """*************************************************
    ************* Pages Initialization *****************
    *************************************************"""
    def _initialize_page_serial_number(self):
        pass

    def _initialize_page_connect_udc(self):
        pass

    def _initialize_page_load_test_firmware(self):
        pass

    def _initialize_page_start_test(self):
        self.teTestReport.clear()

    def _initialize_page_load_final_firmware(self):
        pass

    def _initialize_page_test_finished(self):
        pass

    """*************************************************
    ************** Pages Validation ********************
    *************************************************"""
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

    def _validate_page_connect_udc(self):
        return True

#    def _validate_page_visual_test(self):
#        if (self.rbLedsOk.isChecked() or self.rbLedsNok.isChecked()) and \
#            (self.rbBuzzerOk.isChecked() or self.rbBuzzerNok.isChecked()):
#
#            if self.rbLedsOk.isChecked():
#                self._test_thread.led = self.SUCCESS
#            else:
#                self._test_thread.led = self.FAIL
#
#            if self.rbBuzzerOk.isChecked():
#                self._test_thread.buzzer = self.SUCCESS
#            else:
#                self._test_thread.buzzer = self.FAIL
#
#            return True
#
#        return False

    def _validate_page_load_test_firmware(self):
        self._leds_status = self.rbLedsOk.isChecked()
        self._buzzer_status = self.rbBuzzerOk.isChecked()

        if self._load_test_firmware_status and self._leds_status \
            and self._buzzer_status and self._communication_status:
            return True
        else:
            # TODO: Mandar dados para o servidor
            self._restart_variables()
            self._initialize_widgets()
            self._jump_to(self.num_serial_number)
            return False

    def _validate_page_start_test(self):
        if self._test_result:
            return True
        else:
            self._initialize_widgets()
            self._restart_test_thread()
            self._jump_to(self.num_serial_number)
            return False

    def _validate_page_load_final_firmware(self):
        if self._load_final_firmware_status:
            self._initialize_widgets()
            self._restart_test_thread()
            self._jump_to(self.num_serial_number)
        return False

    def _validate_page_test_finished(self):
        return True

    """*************************************************
    *********** Default Methods (Wizard) ***************
    *************************************************"""
    def initializePage(self, page):
        if page == self.num_serial_number:
            self._initialize_page_serial_number()

        elif page == self.num_connect_udc:
            self._initialize_page_connect_udc()

        elif page == self.num_load_test_firmware:
            self._initialize_page_load_test_firmware()

        elif page == self.num_start_test:
            self._initialize_page_start_test()

        elif page == self.num_load_final_firmware:
            self._initialize_page_load_final_firmware()

        elif page == self.num_test_finished:
            self._initialize_page_test_finished()

        else:
            pass

    def validateCurrentPage(self):
        current_id = self.currentId()
        if current_id == self.num_serial_number:
            return self._validate_page_serial_number()

        elif current_id == self.num_connect_udc:
            return self._validate_page_connect_udc()

        elif current_id == self.num_load_test_firmware:
            return self._validate_page_load_test_firmware()

        elif current_id == self.num_start_test:
            return self._validate_page_start_test()

        elif current_id == self.num_load_test_firmware:
            return self._validate_page_load_test_firmware()

        elif current_id == self.num_test_finished:
            return self._validate_page_test_finished()

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
    def _load_test_firmware(self):
        arm_status = False
        c28_status = False
        fw = LoadFirmware()

        fw.arm_pathtofile = "/firmware/test/m3_test.out" #Ver nome
        fw.c28_pathtofile = "/firmware/test/c28_test.out" #Ver nome

        self.teTestFirmwareLog.append("Gravando firmware de testes ARM:\n")
        fw.flash_firmware('arm')
        self.teTestFirmwareLog.append(fw.log_status)
        print(fw.status)
        if fw.status is "sucess":
            arm_status = True
        self.teTestFirmwareLog.append("Gravando firmware de testes C28:\n")
        fw.flash_firmware('c28')
        self.teTestFirmwareLog.append(fw.log_status)
        print(fw.status)
        if fw.status is "sucess":
            c28_status = True

        if arm_status and c28_status:
            self._load_test_firmware_status = True
        else:
            self._load_test_firmware_status = False

    @pyqtSlot()
    def _load_final_firmware(self):
        arm_status = False
        c28_status = False
        fw = LoadFirmware()

        fw.arm_pathtofile = "/firmware/final/c28_final.out" #Ver nome
        fw.c28_pathtofile = "/firmware/final/m3_final.out" #Ver nome

        self.teFinalFirmwareLog.append("Gravando firmware de testes ARM:\n")
        fw.flash_firmware('arm')
        self.teFinalFirmwareLog.append(fw.log_status)
        print(fw.status)
        if fw.status is "sucess":
            arm_status = True
        self.teFinalFirmwareLog.append("Gravando firmware de testes C28:\n")
        fw.flash_firmware('c28')
        self.teFinalFirmwareLog.append(fw.log_status)
        print(fw.status)
        if fw.status is "sucess":
            c28_status = True

        if arm_status and c28_status:
            self._load_final_firmware_status = True
        else:
            self._load_final_firmware_status = False

    @pyqtSlot()
    def _connect_serial_port(self):
        com = str(self.comboComPort.currentText())
        baud = int(self.leBaudrate.text())
        self._test_thread.baudrate = baud
        self._test_thread.comport  = com
        self._serial_port_status    = self._test_thread.open_serial_port()
        if self._serial_port_status:
            self.pbConnectSerialPort.setEnabled(False)
            self.pbConnectSerialPort.setText("Conectado!")
        self._communication_status  = self._test_thread.test_communication()
        if self._communication_status:
            self.lbStatusComunicacao.setText("OK")
        else:
            self.lbStatusComunicacao.setText("Falha")


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

    @pyqtSlot(list)
    def _update_io_expander_label(self, value):
        self.lbExpansorIO1.setText(value[0])
        self.lbExpansorIO2.setText(value[1])

    @pyqtSlot(list)
    def _update_ethernet_label(self, value):
        self.lbEthernetInit.setText(value[0])
        self.lbEthernetPing.setText(value[1])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = UDCWindow()
    gui.show()
    sys.exit(app.exec_())

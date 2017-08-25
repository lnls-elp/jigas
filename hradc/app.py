#!/usr/bin/python3
from PyQt5.QtWidgets import QWizard, QApplication, QWizardPage
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from common.dmscanner import Scanner
from common.flashfirmware import LoadFirmware_HRADC
from PyQt5.uic import loadUiType
from hradctest import HRADCTest
import serial
import glob
import sys

UI_PATH = 'wizard.ui'
Ui_Class, base = loadUiType(UI_PATH)

class HRADCWindow(QWizard, Ui_Class):

    # Page numbers
    (num_intro_page, num_serial_number, num_connect_hradc,
    num_load_firmware, num_start_test) = range(5)

    def __init__(self, parent=None):
        QWizard.__init__(self, parent)
        self.setupUi(self)

        self._SERIAL_BAUDRATE = 6000000

        self._list_serial_ports()
        self._serial_port_status = False
        self._test_communication_status = False

        self._status_load_firmware = False

        self._boardsinfo = []

        self._test_thread = HRADCTest()

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
        self.rbLedStatusOk.setChecked(False)
        self.rbLedStatusNok.setChecked(False)
        self.rbLedAlimOk.setChecked(False)
        self.rbLedAlimNok.setChecked(False)
        self.teFirmwareLog.clear()
        self.lbTestStatus.setText("Clique para Iniciar Testes")
        self.lbTestResult1.setText("Aguarde...")
        self.lbTestResult2.setText("Aguarde...")
        self.lbTestResult3.setText("Aguarde...")
        self.lbTestResult4.setText("Aguarde...")
        self.teTestReport.clear()

    def _new_board_widgets_init(self):
        self.leDmCode.clear()
        self.leSerialNumber.setReadOnly(True)
        self.leSerialNumber.clear()
        self.leMaterialCode.setReadOnly(True)
        self.leMaterialCode.clear()
        self.lbStatusComunicacao.setText("...")
        self.rbLedStatusOk.setChecked(False)
        self.rbLedStatusNok.setChecked(False)
        self.rbLedAlimOk.setChecked(False)
        self.rbLedAlimNok.setChecked(False)
        self.lbTestResult1.setText("Aguarde...")
        self.lbTestResult2.setText("Aguarde...")
        self.lbTestResult3.setText("Aguarde...")
        self.lbTestResult4.setText("Aguarde...")
        self.cbEndTests.clear()

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.leDmCode.editingFinished.connect(self._treat_dmcode)
        #self.rbLedStatusNok.toggled.connect(self._treat_leds_nok)
        self.pbLoadFirmware.clicked.connect(self._load_firmware)
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

        self.PageConnectHradc.setButtonText(self.NextButton, "Próximo")
        self.PageConnectHradc.setButtonText(self.BackButton, "Anterior")
        self.PageConnectHradc.setButtonText(self.CancelButton, "Cancelar")

        self.PageLoadFirmware.setButtonText(self.NextButton, "Próximo")
        self.PageLoadFirmware.setButtonText(self.BackButton, "Anterior")
        self.PageLoadFirmware.setButtonText(self.CancelButton, "Cancelar")

        self.PageStartTest.setButtonText(self.NextButton, "Novo Teste")
        self.PageStartTest.setButtonText(self.BackButton, "Anterior")
        self.PageStartTest.setButtonText(self.CancelButton, "Cancelar")

        self.button(self.NextButton).clearFocus()
        self.button(self.BackButton).clearFocus()
        self.button(self.CancelButton).clearFocus()

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
        self._test_communication_status = False
        del self._boardsinfo[:]

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

    def _initialize_page_connect_hradc(self):
        pass

    def _initialize_page_load_firmware(self):
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
        variant = self.leMaterialCode.text()
        scan = Scanner()

        try:
            if not int(serial) in [board['serial'] for board in self._boardsinfo]:

                board = {}
                board['serial'] = int(serial)
                board['variant'] = scan.get_material_name(variant)
                board['pre_tests'] = ''

                try:
                    board['slot'] = max(0,max([board['slot'] for board in self._boardsinfo]))+1
                except:
                    board['slot'] = 1

                if not variant in scan.materiais:
                    raise ValueError

                self._boardsinfo.append(board)

            self.rbLedAlimOk.setChecked(False)
            self.rbLedAlimNok.setChecked(False)

            return True


        except ValueError:
            pass

        return False

    def _validate_page_connect_hradc(self):
        if self.rbLedAlimOk.isChecked():
            self.rbLedStatusOk.setChecked(False)
            self.rbLedStatusNok.setChecked(False)
            return True

        elif self.rbLedAlimNok.isChecked():
            self._boardsinfo[-1]['pre_tests'] = self._boardsinfo[-1]['pre_tests'] + '\t' + 'Erro: Falha LEDs +/-15V'
            self._boardsinfo[-1]['slot'] = -abs(self._boardsinfo[-1]['slot'])

            print(self._boardsinfo[-1])
            print('Falhou LED +/-15V')
            self.rbLedStatusOk.setChecked(False)
            self.rbLedStatusNok.setChecked(False)
            self._new_board_widgets_init()
            while self.currentId() is not self.num_serial_number:
                self.back()

        return False

    def _validate_page_load_firmware(self):
        if self._status_load_firmware:

            if self._test_communication_status:

                if not self.rbLedStatusOk.isChecked() and not self.rbLedStatusNok.isChecked():
                    return False

                elif self.rbLedStatusOk.isChecked():

                    if self._boardsinfo[-1]['slot'] < 4 and not self.cbEndTests.isChecked():
                        self._new_board_widgets_init()
                        self._status_load_firmware = False
                        self._test_communication_status = False
                        self.lbStatusComunicacao.setText("...")
                        while self.currentId() is not self.num_serial_number:
                            self.back()
                    else:
                        self._test_thread._boardsinfo = self._boardsinfo[:]
                        self._new_board_widgets_init()
                        return True

                if self.rbLedStatusNok.isChecked():

                    self._boardsinfo[-1]['pre_tests'] = self._boardsinfo[-1]['pre_tests'] + '\t' + 'Erro: Falha LED Status'
                    self._boardsinfo[-1]['slot'] = -abs(self._boardsinfo[-1]['slot'])
                    self._status_load_firmware = False
                    self._test_communication_status = False
                    self.lbStatusComunicacao.setText("...")
                    print(self._boardsinfo[-1])
                    print('Falhou LED Status')

                    if self.cbEndTests.isChecked():
                        self._test_thread._boardsinfo = self._boardsinfo[:]
                        self._new_board_widgets_init()
                        return True

                    else:
                        self._new_board_widgets_init()
                        while self.currentId() is not self.num_serial_number:
                            self.back()

            elif self._boardsinfo[-1]['slot'] < 0:
                self._status_load_firmware = False
                self._test_communication_status = False
                self.lbStatusComunicacao.setText("...")
                print(self._boardsinfo[-1])
                print('Falhou gravação de firmware')
                while self.currentId() is not self.num_serial_number:
                    self.back()

        return False

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

        elif page == self.num_load_firmware:
            self._initialize_page_load_firmware()

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

        elif current_id == self.num_load_firmware:
            return self._validate_page_load_firmware()

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
            aux = scan.get_material_name(data['material'])
            self.leMaterialName.setText(aux)
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
        slot = abs(self._boardsinfo[-1]['slot'])

        if self._status_load_firmware:
            result = self._test_thread.test_communication(slot)
            if result:
                self._boardsinfo[-1]['slot'] = slot
                self.lbStatusComunicacao.setText("<p color:'green'>OK</p>")
            else:
                self._boardsinfo[-1]['pre_tests'] = self._boardsinfo[-1]['pre_tests'] + '\t' + 'Erro: Falha de comunicação com CPLD'
                self._boardsinfo[-1]['slot'] = -slot
                self.lbStatusComunicacao.setText("<p color:'red'>Falha</p>")

            self._test_communication_status = True

        else:
            self._test_communication_status = False

    '''
    @pyqtSlot()
    def _treat_leds_nok(self):
        if self.rbLedStatusNok.isChecked():
            self.pbLoadFirmware.setEnabled(False)
        else:
            self.pbLoadFirmware.setEnabled(True)
    '''

    @pyqtSlot()
    def _start_test_sequence(self):
        self._test_thread.test_complete.connect(self._test_finished)
        self._test_thread.update_gui.connect(self._update_test_log)
        self._test_thread.start()

    @pyqtSlot()
    def _finish_wizard_execution(self):
        pass


    @pyqtSlot()
    def _load_firmware(self):
        qts = LoadFirmware_HRADC()
        result = qts.load_firmware()

        slot = abs(self._boardsinfo[-1]['slot'])

        if 'sucesso' in result:
            self._boardsinfo[-1]['slot'] = slot
        else:
            self._boardsinfo[-1]['slot'] = -slot

        self.teFirmwareLog.append('Slot ' + str(slot) + ' - S/N ' + str(self._boardsinfo[-1]['serial']) + ' : ' + result)
        self._boardsinfo[-1]['pre_tests'] = self._boardsinfo[-1]['pre_tests'] + '\t' + result

        self._status_load_firmware = True

    @pyqtSlot(list)
    def _test_finished(self, result):

        if result[0] is not None:
            self.lbTestResult1.setText(result[0])
        else:
            self.lbTestResult1.setText("NC")

        if result[1] is not None:
            self.lbTestResult2.setText(result[1])
        else:
            self.lbTestResult2.setText("NC")

        if result[2] is not None:
            self.lbTestResult3.setText(result[2])
        else:
            self.lbTestResult3.setText("NC")

        if result[3] is not None:
            self.lbTestResult4.setText(result[3])
        else:
            self.lbTestResult4.setText("NC")

    @pyqtSlot(str)
    def _update_test_log(self, value):
        self.teTestReport.append(value)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = HRADCWindow()
    gui.show()
    sys.exit(app.exec_())

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.elpwebclient import ElpWebClient
from udcdata import UDC, UDCLog
import serial
import random

class UDCTest(QThread):
    FAIL        = "Falha"
    SUCCESS     = "OK"

    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    eeprom              = pyqtSignal(str)
    flash               = pyqtSignal(str)
    ram                 = pyqtSignal(str)
    adc                 = pyqtSignal(list)
    rtc_com             = pyqtSignal(str)
    rtc_int             = pyqtSignal(str)
    sensor_temp_com     = pyqtSignal(str)
    sensor_temp_val     = pyqtSignal(str)
    rs485               = pyqtSignal(list)
    isol_plane          = pyqtSignal(str)
    io_expander         = pyqtSignal(str)
    ethernet            = pyqtSignal(str)

    def __init__(self, comport=None, baudrate=None, serial_number=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._led = None
        self._buzzer = None

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value

    @property
    def buzzer(self):
        return self._buzzer

    @buzzer.setter
    def buzzer(self, value):
        self._buzzer = value

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value

    @property
    def baudrate(self):
        return self._baudarate

    @baudrate.setter
    def baudrate(self, value):
        self._baudrate = value

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            #TODO: Open serial and return StatusCode
            pass

    def test_communication(self):
        result = False     # Result for communication test and aux power supply
        #TODO: Communication test
        """
            Simulação de teste
        """
        result = True
        """
            Fim da Simulação
        """
        return result

    def _test_eeprom(self):
        result = self.FAIL
        #TODO: Testes
        self.eeprom.emit(result)
        return result

    def _test_flash(self):
        result = self.FAIL
        #TODO: Testes
        self.flash.emit(result)
        return result

    def _test_ram(self):
        result = self.FAIL
        #TODO: Testes
        self.ram.emit(result)
        return result

    def _test_adc(self):
        result = [self.FAIL for i in range(8)]
        #TODO: Testes
        self.adc.emit(result)
        return result

    def _test_rtc_communication(self):
        result = self.FAIL
        #TODO: Testes
        self.rtc_com.emit(result)
        return result

    def _test_rtc_interrupt(self):
        result = self.FAIL
        #TODO: Testes
        self.rtc_int.emit(result)
        return result

    def _test_temperature_sensor_communication(self):
        result = self.FAIL
        #TODO: Testes
        self.sensor_temp_com.emit(result)
        return result

    def _test_temperature_sensor_value(self):
        result = self.FAIL
        #TODO: Testes
        self.sensor_temp_val.emit(result)
        return result

    def _test_rs485(self):
        result = [self.FAIL for i in range(3)]
        #TODO: Testes
        self.rs485.emit(result)
        return result

    def _test_alim_isol_plane(self):
        result = self.FAIL
        #TODO: Testes
        self.isol_plane.emit(result)
        return result

    def _test_io_expander(self):
        result = self.FAIL
        #TODO: Testes
        self.io_expander.emit(result)
        return result

    def _test_ethernet(self):
        result = self.FAIL
        #TODO: Testes
        self.ethernet.emit(result)
        return result

    def _test_periph_loopback(self):
        pass

    def _test_sequence(self):
        result = False

        udc = UDC()
        udc.serial_number = self._serial_number
        res = self._send_to_server(udc)

        if res:
            #TODO: Sequencia de Testes
            """
            Simulação de valores
            """
            log = UDCLog()
            log.leds                        = self._led
            log.buzzer                      = self._buzzer
            log.io_expander                 = self._test_io_expander()
            log.eeprom                      = self._test_eeprom()
            log.flash                       = self._test_flash()
            log.ram                         = self._test_ram()
            log.rtc_communication           = self._test_rtc_communication()
            log.rtc_interrupt               = self._test_rtc_interrupt()
            log.temperature_sensor          = self._test_temperature_sensor_value()
            log.control_aliment_isol_plane  = self._test_alim_isol_plane()
            log.rs485                       = self._test_rs485()
            log.test_result = "Aprovado"
            log.serial_number_udc = self._serial_number
            log.details = ""

            result = self._send_to_server(log)

        self.test_complete.emit(result)
        """
            Fim da Simulação
        """

    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        server_status = self._parse_response(client_response)
        return server_status

    def _parse_response(self, response):
        res_key = 'StatusCode'
        err_key = 'error'

        if res_key in response.keys() and err_key not in response.keys():
            return True
        else:
            return False

    def run(self):
        self._test_sequence()
        #pass

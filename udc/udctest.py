from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.elpwebclient import ElpWebClient
from udcdata import UDC, UDCLog
import serial
import random

class UDCTest(QThread):
    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None, serial_number=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._serial_port = serial.Serial()

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

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
            self._serial_port.baudrate  = self._baudrate
            self._serial_port.port      = self._comport
            self._serial_port.open()
            return self._serial_port.is_open

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

    def _test_sequence(self):
        result = False
        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        udc = UDC()
        udc.serial_number = self._serial_number
        res = self._send_to_server(udc)

        if res:
            #TODO: Sequencia de Testes
            """
            Simulação de valores
            """
            log = UDCLog()
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

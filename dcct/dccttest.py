from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from dcctdata import *
from elpwebclient import *
import serial
import random

class DCCTTest(QThread):
    test_complete       = pyqtSignal(bool)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None, serial_number=None, variant=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._variant = variant
        self._serial_port = serial.Serial()

        self._load_current = [0, 2, 4, 6, 8, 10, -10, -8, -6, -4, -2]

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def variant(self):
        return self._variante

    @variant.setter
    def variant(self, value):
        self._variante = value

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
        result = (False, False)     # Result for communication test and aux power supply
        #TODO: Communication test
        """
            Simulação de teste
        """
        result = (True, True)
        """
            Fim da Simulação
        """
        return result

    def _test_sequence(self):
        #result = [None, None]
        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
            # Encerrar Testes

        dcct = DCCT()
        dcct.serial_number = self._serial_number
        dcct.variant = self._variant
        res = self._send_to_server(dcct)

        if res:
            #TODO: Sequencia de Testes
            """
            Simulação de valores
            """
            log = DCCTLog()
            log.id_canal_dcct = 1
            log.test_result = "Aprovado"
            log.serial_number_dcct = self._serial_number
            log.iload0 = random.uniform(1.0, 9.0)
            log.iload1 = random.uniform(1.0, 9.0)
            log.iload2 = random.uniform(1.0, 9.0)
            log.iload3 = random.uniform(1.0, 9.0)
            log.iload4 = random.uniform(1.0, 9.0)
            log.iload5 = random.uniform(1.0, 9.0)
            log.iload6 = random.uniform(1.0, 9.0)
            log.iload7 = random.uniform(1.0, 9.0)
            log.iload8 = random.uniform(1.0, 9.0)
            log.iload9 = random.uniform(1.0, 9.0)
            log.iload10 = random.uniform(1.0, 9.0)
            log.details = ""

            log_res = self._send_to_server(log)

        self.test_complete.emit(log_res)
        """
            Fim da Simulação
        """
        print("FIMMMMM")

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

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.psdata import PowerSupply, PowerSupplyLog
from common.elpwebclient import ElpWebClient
import serial
import random

class BurnInTest(QThread):
    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    test = {'Normal':1, 'Burn-In': 2}

    def __init__(self):
        QThread.__init__(self)
        self._comport = None
        self._baudarate = None
        self._serial_number = []
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
        result = False

        ps = PowerSupply()
        ps.serial_number = self._serial_number
        res = self._send_to_server(ps)

        if res:
            #TODO: Sequencia de Testes
            """
            Simulação de valores
            """
            log = PowerSupplyLog()
            log.test_type = self.test['Burn-In']
            log.id_canal_power_supply = 1
            log.test_result = "Aprovado"
            log.result_test_on_off = "Aprovado"
            log.serial_number_power_supply = 1234
            log.iout0 = random.uniform(1.0, 9.0)
            log.iout1 = random.uniform(1.0, 9.0)
            log.vout0 = random.uniform(1.0, 9.0)
            log.vout1 = random.uniform(1.0, 9.0)
            log.vdclink0 = random.uniform(1.0, 9.0)
            log.vdclink1 = random.uniform(1.0, 9.0)
            log.temperatura0 = random.uniform(1.0, 9.0)
            log.temperatura1 = random.uniform(1.0, 9.0)
            log.iout_add_20_duty_cycle = random.uniform(1.0, 9.0)
            log.iout_less_20_duty_cycle = random.uniform(1.0, 9.0)
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

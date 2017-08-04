from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.hradcdata import HRADC, HRADCLogCalib
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
import time

class HRADCCalib(QThread):

    calib_complete      = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    device = {'HRADC':1, 'DM':2}

    def __init__(self):
        QThread.__init__(self)
        self._comport = None
        self._baudarate = None
        self._serial_number = None

        self._led = None

        self.FBP = SerialDRS()


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

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value


    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):

        result = True

        #TODO: Communication test

        return result

    def _calib_sequence(self):

        hradc = HRADC()
        hradc.serial_number = self._serial_number
        print(hradc.data)
        res = self._send_to_server(hradc)

        if res:
            log = HRADCLogCalib()
            log.serial_number_hradc = self._serial_number
            log.temperature_hradc = 10.0

            print(log.data)
            # TODO: Faz os testes e seta os atributos de log

            """
            Simulação de valores
            """

            log_res = self._send_to_server(log)

            """
            Fim da simulação
            """

            # Quando o teste terminar emitir o resultado em uma lista de objetos
            # do tipo PowerModuleLog
            self.calib_complete.emit(log_res)

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
        self._calib_sequence()
        #pass

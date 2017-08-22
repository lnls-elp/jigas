from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.hradcdata import HRADC, HRADCLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
import time

class HRADCTest(QThread):

    test_complete       = pyqtSignal(list)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    device = {'HRADC':1, 'DM':2}

    def __init__(self):
        QThread.__init__(self)
        self._comport = None
        self._baudrate = None
        self._boardsinfo = []
        self._nHRADC = None
        self._led = None

        self.drs = SerialDRS()


    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, value):
        self._baudrate = value

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
    def firmware_error(self):
        return self._firmware_error

    @firmware_error.setter
    def firmware_error(self, value):
        self._firmware_error = value
        
    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            return self.drs.Connect(self._comport, self._baudrate)

    def test_communication(self):

        result = True

        
        #TODO: Communication test

        return result

    def _test_sequence(self):

        self.nHRADC = max([board['slot'] for board in self._boardsinfo])
        self.drs.Config_nHRADC(self.nHRADC)
        log_res = []
        
        for board in self._boardsinfo:

            hradc = HRADC()

            hradc.serial_number = board['serial']
            hradc.variant = board['variant']
            self._burden_amplifier = "INA141"
            
            if hradc.variant = 'HRADC-FBP':
                hradc.burden_res = 20.0
                self._cut_frequency = 48228.7
                self._filter_order = 1       

            res = self._send_to_server(hradc)

            if res:

                log_hradc = HRADCLog()
                log_hradc.serial_number_hradc = board['serial']
                log_hradc.device = self.device['HRADC']

                log_dm = HRADCLog()                  
                log_dm.serial_number_hradc = board['serial']
                log_dm.device = self.device['DM']
                
                if 'success' in board['pre_tests']:

                    test(board)
                    
                    log_hradc.test_result = "?"
                    log_hradc.details = ""

                    log_dm.test_result = "?"
                    log_dm.details = ""

                    log_hradc_serverstatus = self._send_to_server(log_hradc)
                    log_dm_serverstatus = self._send_to_server(log_dm)

                else:
                    log_hradc.test_result = "Reprovado"
                    log_hradc.details = board['pre_tests']

                    log_hradc_serverstatus = self._send_to_server(log_hradc)

                log_res.append(log_hradc.test_result)                

        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo HRADCLog
        
        for i in range(4 - len(log_res)):
            log_res.append(None)
        self.test_complete.emit(log_res)
        
            
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

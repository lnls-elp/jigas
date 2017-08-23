from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.hradcdata import HRADC, HRADCLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
import time
import struct

class HRADCTest(QThread):

    test_complete       = pyqtSignal(list)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    device = {'HRADC':1, 'DM':2}
    bytesFormat = {'Uint16': 'H', 'Uint32': 'L', 'Uint64': 'Q', 'float': 'f'}
    ufmOffset = {'serial': 0, 'calibdate': 4, 'variant': 9, 'rburden': 10}
    hradcVariant = {'HRADC-FBP': 0, 'HRADC-FAX': 1}

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

    def test_communication(self,slot):
        
        #TODO: Communication test
        return True

    def _test_sequence(self):

        print('Valendo!')
        
        print(self._boardsinfo)
        self.nHRADC = max([board['slot'] for board in self._boardsinfo])
        print('Configurando nHRADC')
        self.drs.Config_nHRADC(self.nHRADC)
        time.sleep(1)
        print('Resetando HRADC')
        self.drs.ResetHRADCBoards(1)
        time.sleep(1)
        self.drs.ResetHRADCBoards(0)
        log_res = []
        
        print('Començando a ler boardsinfo')
        
        for board in self._boardsinfo:
            
            print(board)
            
            hradc = HRADC()
            ufmdata_16 = []
    
            hradc.serial_number = board['serial']
            hradc.variant = board['variant']
            hradc.burden_amplifier = "INA141"
            
            if hradc.variant == 'HRADC-FBP':
                hradc.burden_res = 20.0
                hradc.cut_frequency = 48228.7
                hradc.filter_order = 1       

            print('Enviando ao servidor dados desta placa')
            res = self._send_to_server(hradc)

            if res:
                print(res)

                log_hradc = HRADCLog()
                log_hradc.serial_number_hradc = board['serial']
                log_hradc.device = self.device['HRADC']

                log_dm = HRADCLog()                  
                log_dm.serial_number_hradc = board['serial']
                log_dm.device = self.device['DM']
                
                if board['slot'] > 0:
                    print('Colocando em UFM mode a placa bem sucedida do slot:' + str(board['slot']))

                    board['slot'] = board['slot'] - 1
                    self.drs.ConfigHRADCOpMode(board['slot'],1)
                    time.sleep(0.5)

                    print('Enviando serial number')
                    # Send serial number
                    ufmdata_16 = self._convertToUint16List(board['serial'],'Uint64')
                    print(ufmdata_16)
                    for i in range(len(ufmdata_16)):
                        print(i+self.ufmOffset['serial'])
                        print(ufmdata_16[i])
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['serial'],ufmdata_16[i])
                        time.sleep(0.1)


                    print('Enviando variante')
                    # Send variant
                    ufmdata_16 = self._convertToUint16List(self.hradcVariant[board['variant']],'Uint16')
                    for i in range(len(ufmdata_16)):
                        print(i+self.ufmOffset['variant'])
                        print(ufmdata_16[i])
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['variant'],ufmdata_16[i])
                        time.sleep(0.1)

                    print('Enviando rburden')
                    # Send Rburden
                    print(hradc.burden_res)
                    ufmdata_16 = self._convertToUint16List(hradc.burden_res,'float')
                    print(ufmdata_16)
                    for i in range(len(ufmdata_16)):
                        print(i+self.ufmOffset['rburden'])
                        print(ufmdata_16[i])
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['rburden'],ufmdata_16[i])
                        time.sleep(0.1) 

                    print('Lendo byte')
                    time.sleep(0.5)
                    self.drs.ReadHRADC_UFM(board['slot'],0)


                    print('Salvando log e enviando ao servidor')
                    log_hradc.details = board['pre_tests']
                    log_hradc.test_result = "Aprovado"
                    
                    log_dm.test_result = "Aprovado"

                    log_hradc_serverstatus = self._send_to_server(log_hradc)
                    log_dm_serverstatus = self._send_to_server(log_dm)

                    log_res.append(log_hradc.test_result) 

                else:
                    print('Salvando log de placa reprovada enviando ao servidor')
                    log_hradc.test_result = "Reprovado"
                    log_hradc.details = board['pre_tests']

                    log_hradc_serverstatus = self._send_to_server(log_hradc)
                              

        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo HRADCLog

        print('Enviando sinal ao app')
        
        for i in range(4 - len(log_res)):
            log_res.append(None)
        print('log_res:' + str(log_res))
        self.test_complete.emit(log_res)
        
            
    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        print('client_data:\n')
        print(client_data)
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

    def _convertToUint16List(self, val, format):

        val_16 = []
        val_b = struct.pack(self.bytesFormat[format],val)
        print(val_b)
        for i in range(0,len(val_b),2):
            val_16.append(struct.unpack('H',val_b[i:i+2])[0])
        print(val_16)
        return val_16
            
    def run(self):
        self._test_sequence()
        #pass

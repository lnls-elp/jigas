from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.elpwebclient import ElpWebClient
from rackdata import Rack, RackLog
from common.pydrs import SerialDRS
import serial
import random
import time

class RackTest(QThread):
    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None, serial_number=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        #self._serial_port = serial.Serial()
        self.FBP = SerialDRS()

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
            self.FBP.SetSlaveAdd(1)
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):
        result = False     # Result for communication test

        try:
            self.FBP.Write_sigGen_Aux(0)
            test_package = self.FBP.Read_ps_Model()
            if (test_package[0] == 0) and (test_package[1] == 17) and (test_package[2] == 512) and (test_package[3] == 14) and (test_package[4] == 223):
                result = True
            else:
                result = False
        except:
            result = False

        return result

    def _test_sequence(self):
        result     = False
        test_setup = False
        list_iout0 = []
        list_iout1 = []
        list_iout2 = []
        list_iout3 = []

        rack = Rack()
        rack.serial_number = self._serial_number
        res = self._send_to_server(rack)

        if res:
            #TODO: Sequencia de Testes

            self.FBP.Write_sigGen_Aux(0) # Usando 0 modulos de potência
            log = RackLog()

            for i in range(0, 10):
                list_iout0.append(self.FBP.Read_iMod1())
                list_iout1.append(self.FBP.Read_iMod2())
                list_iout2.append(self.FBP.Read_iMod3())
                list_iout3.append(self.FBP.Read_iMod4())
                time.sleep(60) # Alterar para 60s
                self.update_gui.emit('leitura ' + str(i+1) + ':')
                self.update_gui.emit('iout0 = ' + str(list_iout0[i]) + ' A')
                self.update_gui.emit('iout1 = ' + str(list_iout1[i]) + ' A')
                self.update_gui.emit('iout2 = ' + str(list_iout2[i]) + ' A')
                self.update_gui.emit('iout3 = ' + str(list_iout3[i]) + ' A')

                if (abs(round(list_iout0[i]))>=12) or (abs(round(list_iout1[i]))>=12) \
                    or (abs(round(list_iout2[i]))>=12) or (abs(round(list_iout3[i]))>=12):
                    self.update_gui.emit('ERRO: REPITA O PROCEDIMENTO DE CONEXÕES DO BASTIDOR E INICIE UM NOVO TESTE')
                    test_setup = False
                    break
                else:
                    test_setup = True

            if test_setup:
                for j in range(0, 10):
                    if (round(list_iout0[j])==-2) and (round(list_iout1[j])==1) and (round(list_iout2[j])==3) and (round(list_iout3[j])==-3):
                        log.test_result = 'Aprovado'
                        result = True
                    else:
                        log.test_result = 'Reprovado'
                        result = False
                        break
                if result:
                    self.update_gui.emit('Aprovado')
                else:
                    self.update_gui.emit('Reprovado')

                log.iout0       = sum(list_iout0)/len(list_iout0)
                log.iout1       = sum(list_iout1)/len(list_iout1)
                log.iout2       = sum(list_iout2)/len(list_iout2)
                log.iout3       = sum(list_iout3)/len(list_iout3)
                log.delta_iout0 = max(list_iout0) - min(list_iout0)
                log.delta_iout1 = max(list_iout1) - min(list_iout1)
                log.delta_iout2 = max(list_iout2) - min(list_iout2)
                log.delta_iout3 = max(list_iout3) - min(list_iout3)

                log.serial_number_rack = self._serial_number
                log.details            = ""

                if self._send_to_server(log):
                    self.update_gui.emit('Dados enviados para o servidor')
                else:
                    self.update_gui.emit('Erro no envio de dados para o servidor')

                # ao finalizar, emitir signals
                self.test_complete.emit(result)

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

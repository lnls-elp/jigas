from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.elpwebclient import ElpWebClient
from dcctdata import DCCT, DCCTLog
import serial
import random
import pyDRS
import time

class DCCTTest(QThread):
    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None, serial_number=None, variant=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._variant = variant
        self._serial_port = serial.Serial()
        self.FBP = pyDRS.SerialDRS()

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
            #self._serial_port.open()
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):
        result = (False, False)     # Result for communication test and aux power supply
        #TODO: Communication test
        self.FBP.Write_sigGen_Aux(1)

        if type(self.FBP.Read_vDCMod1()) == float:
            result = (True,True)
        else:
            result = (False, False)

        return result

    def _test_sequence(self):
        result = False
        list_log = []
        current_DCCT  = []
        current_DCCT1 = []
        current_DCCT2 = []

        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        dcct = DCCT()
        dcct.serial_number = self._serial_number
        dcct.variant = self._variant
        res = self._send_to_server(dcct)

        if res:
            #TODO: Sequencia de Testes

            #self.FBP = pyDRS.SerialDRS()
            #self.FBP.Connect(self._comport, self._baudarate)
            self.FBP.Write_sigGen_Aux(1) # Usando 1 modulo de potência
            self.FBP.TurnOn()
            self.update_gui.emit('Fonte ligada')
            self.FBP.ClosedLoop()
            self.update_gui.emit('Malha fechada')

            if self._variant == 'CONF A':
                list_log.append(DCCTLog())
                list_log.append(DCCTLog())

                for i in self._load_current:
                    self.FBP.SetISlowRef(i)
                    self.update_gui.emit('Testando DCCTs com corrente de ' + str(i) + 'A')
                    time.sleep(2) # Alterar para 30s
                    current_DCCT1.append(self.FBP.Read_iMod3())
                    current_DCCT2.append(self.FBP.Read_iMod4())

                current_DCCT.append(current_DCCT1)
                current_DCCT.append(current_DCCT2)

                for j in range(0, 2):
                    for k in range(0, len(self._load_current)):
                        if round(current_DCCT[j][k]) == self._load_current[k]:
                            string_result = 'Aprovado'
                            result = True
                        else:
                            string_result = 'Reprovado'
                            result = False
                            break
                    list_log[j].test_result = string_result
                    self.update_gui.emit('DCCT' + str(j+1) + ' ' + str(list_log[j].test_result))

                for l in range(0, 2):
                    list_log[l].iload0 = current_DCCT[l][0]
                    list_log[l].iload1 = current_DCCT[l][1]
                    list_log[l].iload2 = current_DCCT[l][2]
                    list_log[l].iload3 = current_DCCT[l][3]
                    list_log[l].iload4 = current_DCCT[l][4]
                    list_log[l].iload5 = current_DCCT[l][5]
                    list_log[l].iload6 = current_DCCT[l][6]
                    list_log[l].iload7 = current_DCCT[l][7]
                    list_log[l].iload8 = current_DCCT[l][8]
                    list_log[l].iload9 = current_DCCT[l][9]
                    list_log[l].iload10 = current_DCCT[l][10]
                    list_log[l].id_canal_dcct = l+1
                    list_log[l].serial_number_dcct = self._serial_number

                if self._send_to_server(list_log[0]):
                    self.update_gui.emit('Dados enviados para o servidor')
                else:
                    self.update_gui.emit('Erro no envio de dados para o servidor')

                if self._send_to_server(list_log[1]):
                    self.update_gui.emit('Dados enviados para o servidor')
                else:
                    self.update_gui.emit('Erro no envio de dados para o servidor')

            elif self._variant == 'CONF B':
                list_log.append(DCCTLog())
                list_log.append(None)

                for i in self._load_current:
                    self.FBP.SetISlowRef(i)
                    self.update_gui.emit('Testando DCCTs com corrente de ' + str(i) + 'A')
                    time.sleep(2) # Alterar para 30s
                    current_DCCT1.append(self.FBP.Read_iMod3())

                for j in range(0, len(self._load_current)):
                    if round(current_DCCT1[j]) == self._load_current[j]:
                        string_result = 'Aprovado'
                        result = True
                    else:
                        string_result = 'Reprovado'
                        result = False
                        break
                list_log[0].test_result = string_result
                self.update_gui.emit('DCCT1 ' + str(list_log[0].test_result))

                list_log[0].iload0 = current_DCCT1[0]
                list_log[0].iload1 = current_DCCT1[1]
                list_log[0].iload2 = current_DCCT1[2]
                list_log[0].iload3 = current_DCCT1[3]
                list_log[0].iload4 = current_DCCT1[4]
                list_log[0].iload5 = current_DCCT1[5]
                list_log[0].iload6 = current_DCCT1[6]
                list_log[0].iload7 = current_DCCT1[7]
                list_log[0].iload8 = current_DCCT1[8]
                list_log[0].iload9 = current_DCCT1[9]
                list_log[0].iload10 = current_DCCT1[10]

                if self._send_to_server(list_log[0]):
                    self.update_gui.emit('Dados enviados para o servidor')
                else:
                    self.update_gui.emit('Erro no envio de dados para o servidor')

            self.FBP.TurnOff()
            self.FBP.Disconnect()


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

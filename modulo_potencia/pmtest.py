from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from pmdata import PowerModule, PowerModuleLog
from common.elpwebclient import ElpWebClient
import serial
import random
import pyDRS
import time

class PowerModuleTest(QThread):
    test_complete       = pyqtSignal(list)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None,
                    mod0=None, mod1=None, mod2=None, mod3=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_mod0 = mod0
        self._serial_mod1 = mod1
        self._serial_mod2 = mod2
        self._serial_mod3 = mod3
        self._serial_port = serial.Serial()
        self.FBP = pyDRS.SerialDRS()


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
    def serial_mod0(self):
        return self._serial_mod0

    @serial_mod0.setter
    def serial_mod0(self, value):
        self._serial_mod0 = value

    @property
    def serial_mod1(self):
        return self._serial_mod1

    @serial_mod1.setter
    def serial_mod1(self, value):
        self._serial_mod1 = value

    @property
    def serial_mod2(self):
        return self._serial_mod2

    @serial_mod2.setter
    def serial_mod2(self, value):
        self._serial_mod2 = value

    @property
    def serial_mod3(self):
        return self._serial_mod3

    @serial_mod3.setter
    def serial_mod3(self, value):
        self._serial_mod3 = value

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            self._serial_port.baudrate  = self._baudrate
            self._serial_port.port      = self._comport
            #self._serial_port.open()
            #return self._serial_port.is_open
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):
        # Resultado teste de comunicação para os 4 módulos
        n_mod  = 0
        result = [None for i in range(4)]
        serial = [self._serial_mod0, self._serial_mod1, self._serial_mod2,
                    self._serial_mod3]

        for j in range(0, len(serial)):
            if serial[j] != None:
                n_mod = n_mod+1

        try:
            self.FBP.Write_sigGen_Aux(n_mod)
            test_package = self.FBP.Read_ps_Model()

            if (test_package[0] == 0) and (test_package[1] == 17) and (test_package[2] == 512) and (test_package[3] == 14) and (test_package[4] == 223):
                for k in range(0, len(serial)):
                    if serial[k] != None:
                        if k+1 == 1:
                            if round(self.FBP.Read_vDCMod1()) == 15: # Para um DCLink de 15V
                                result[k] = 'OK'
                            else:
                                result[k] = 'Falha'
                        elif k+1 == 2:
                            if round(self.FBP.Read_vDCMod2()) == 15: # Para um DCLink de 15V
                                result[k] = 'OK'
                            else:
                                result[k] = 'Falha'
                        elif k+1 == 3:
                            if round(self.FBP.Read_vDCMod3()) == 15: # Para um DCLink de 15V
                                result[k] = 'OK'
                            else:
                                result[k] = 'Falha'
                        elif k+1 == 4:
                            if round(self.FBP.Read_vDCMod4()) == 15: # Para um DCLink de 15V
                                result[k] = 'OK'
                            else:
                                result[k] = 'Falha'
                    else:
                        result[k] = 'Sem Fonte'
            else:
                result = ['Falha', 'Falha', 'Falha', 'Falha']
        except:
            result = ['Falha Comunicação', 'Falha Comunicação', 'Falha Comunicação', 'Falha Comunicação']

        return result

    def _test_sequence(self):
        response = [None for i in range(4)]

        serial = [self._serial_mod0, self._serial_mod1, self._serial_mod2,
                    self._serial_mod3]

        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        for item in serial:
            if item is not None:
                power_module = PowerModule()
                power_module.serial_number = item
                res = self._send_to_server(power_module)

                if res:

                    log = PowerModuleLog()
                    log.serial_number_power_module = item

                    # TODO: Faz os testes e seta os atributos de log

                    """
                    Simulação de valores
                    """
                    log.test_result = "Aprovado"
                    log.iload0 = random.uniform(1.0, 15.0)
                    log.iload1 = random.uniform(1.0, 15.0)
                    log.iload2 = random.uniform(1.0, 15.0)
                    log.iload3 = random.uniform(1.0, 15.0)
                    log.iload4 = random.uniform(1.0, 15.0)
                    log.iload5 = random.uniform(1.0, 15.0)
                    log.vload0 = random.uniform(1.0, 15.0)
                    log.vload1 = random.uniform(1.0, 15.0)
                    log.vload2 = random.uniform(1.0, 15.0)
                    log.vload3 = random.uniform(1.0, 15.0)
                    log.vload4 = random.uniform(1.0, 15.0)
                    log.vload5 = random.uniform(1.0, 15.0)
                    log.vdclink0 = random.uniform(1.0, 15.0)
                    log.vdclink1 = random.uniform(1.0, 15.0)
                    log.vdclink2 = random.uniform(1.0, 15.0)
                    log.vdclink3 = random.uniform(1.0, 15.0)
                    log.vdclink4 = random.uniform(1.0, 15.0)
                    log.vdclink5 = random.uniform(1.0, 15.0)
                    log.temperatura0 = random.uniform(1.0, 15.0)
                    log.temperatura1 = random.uniform(1.0, 15.0)
                    log.temperatura2 = random.uniform(1.0, 15.0)
                    log.temperatura3 = random.uniform(1.0, 15.0)
                    log.temperatura4 = random.uniform(1.0, 15.0)
                    log.temperatura5 = random.uniform(1.0, 15.0)
                    log.details = ""

                    log_res = self._send_to_server(log)
                    response[serial.index(item)] = log_res
                    """
                    Fim da simulação
                    """

        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo PowerModuleLog
        self.test_complete.emit(response)

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

from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from pmdata import PowerModule, PowerModuleLog
from elpwebclient import ElpWebClient
import serial
import random

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
            self._serial_port.open()
            return self._serial_port.is_open

    def test_communication(self):
        # Resultado teste de comunicação para os 4 módulos
        result = [None for i in range(4)]
        #TODO: Communication test
        """
            Simulação
        """
        result = ["OK", "Falha", "OK", "OK"]
        """
            Fim da simulação
        """
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

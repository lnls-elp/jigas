from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.psdata import PowerSupply, PowerSupplyLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
import time

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
        self._ps_address = 1
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
            #self._serial_port.baudrate  = self._baudrate
            #self._serial_port.port      = self._comport
            #self._serial_port.open()
            #return self._serial_port.is_open
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self, ps_address):
        result = False     # Result for communication test and aux power supply
        self.FBP.SetSlaveAdd(ps_address)
        time.sleep(1)

        try:
            self.FBP.Write_sigGen_Aux(4)
            test_package = self.FBP.Read_ps_Model()

            if (test_package[0] ==   0) and \
               (test_package[1] ==  17) and \
               (test_package[2] == 512) and \
               (test_package[3] ==  14) and \
               (test_package[4] == 223):
                result = True
            else:
                result = False
        except:
            result = False
            print('Falha na comunicação')

        return result

    def find_address(self):
        test_address = 1

        while (self.test_communication(test_address) == False):
            print(test_address)
            test_address = test_address + 1

        print('o endereço da fonte é: ' + str(test_address))
        return test_address

    def set_address(self):
        write_gui  = []
        ps_address = self.find_address()
        self.FBP.SetSlaveAdd(ps_address)
        write_gui.append(str(self._ps_address))

        if self.test_communication(ps_address):
            self.FBP.SetRSAddress(self.write_address)

            if self.test_communication(self._ps_address):
                write_gui.append('endereço ' + str(self._ps_address) + ' gravado com sucesso')
                print('endereço ' + str(self._ps_address) + ' gravado com sucesso')
                self._ps_address = self._ps_address + 1
            else:
                write_gui.append('erro na gravação do endereço')
                print('erro na gravação do endereço')

        return write_gui

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

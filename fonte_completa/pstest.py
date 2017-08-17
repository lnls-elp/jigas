from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from psdata import PowerSupply, PowerSupplyLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
import time

class PowerSupplyTest(QThread):
    test_complete       = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None, serial_number=None, variant=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._serial_port = serial.Serial()
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
            self._serial_port.baudrate  = self._baudrate
            self._serial_port.port      = self._comport
            #self._serial_port.open()
            #return self._serial_port.is_open
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):
        result = (False, False) # Result for communication test and aux power supply
        test = []
        #TODO: Communication test

        for i in range(2):
            try:
                self.FBP.SetSlaveAdd(i+1) # Endereço do controlador
                self.FBP.Write_sigGen_Aux(4 - (4 * i)) # Usando 4 fontes no bastidor
                                                       # em teste e 0 na jiga bastidor
                test_package = self.FBP.Read_ps_Model()

                if (test_package[0] == 0)   and (test_package[1] == 17) and \
                   (test_package[2] == 512) and (test_package[3] == 14) and \
                   (test_package[4] == 223):
                    test.append(True)
                else:
                    test.append(False)
            except:
                test.append(False)

        if test == [True, True]:
            result = (True, True)
        else:
            result = (False, False)
        return result

    def _test_sequence(self):
        result = False
        test     = [[] for i in range(4)]
        MeasCurr = [[[] for j in range(5)] for k in range(4)]

        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        ps = PowerSupply()
        ps.serial_number = self._serial_number
        res = self._send_to_server(ps)

        if res:
            self.FBP.SetSlaveAdd(1) # Bastidor a ser testado

            '''########################### Teste Liga/Desliga ###########################'''
            '''##########################################################################'''
            for modulo in range(4):
                self.update_gui.emit('Iniciando teste liga/desliga dos módulos de potência...')
                self.FBP.TurnOn(2**modulo)
                self.FBP.OpenLoop(2**modulo)
                time.sleep(1)

                if self.FBP.Read_ps_OnOff() == 2 ** modulo:
                    test[modulo].append(True)
                else:
                    test[modulo].append(False)
                    self.update_gui.emit('O módulo ' + str(modulo + 1) + ' não ligou corretamente')

                self.TurnOff(2**modulo)

                if self.FBP.Read_ps_OnOff() == 0:
                    test[modulo].append(True)
                else:
                    test[modulo].append(False)
                    self.update_gui.emit('O módulo ' + str(modulo + 1) + ' não desligou corretamente')
                time.sleep(1)
            '''##########################################################################'''


            '''#################### Teste em Malha Aberta com 20% #######################'''
            '''##########################################################################'''
            self.FBP.TurnOn(0b1111)   # liga todos os módulos
            self.FBP.OpenLoop(0b1111) # todos os módulos em malha aberta
            self.FBP.OpMode(2)        # coloca a fonte no modo WfmRef para setar as correntes individualmente

            for modulo in range(4):
                self.FBP.ConfigWfmRef(modulo+1, 20) # ajusta 20% do ciclo de trabalho apenas para o modulo testado
                self.FBP.WfmRefUpdate()

                time.sleep(5)

                if modulo == 0:
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod1()) # corrente de saída lida pelo bastidor testado
                    self.FBP.SetSlaveAdd(5) # jiga bastidor
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod1()) # corrente de saída lida pela jiga bastidor

                elif modulo == 1:
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod2()) # corrente de saída lida pelo bastidor testado
                    self.FBP.SetSlaveAdd(5) # jiga bastidor
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod2()) # corrente de saída lida pela jiga bastidor

                elif modulo == 2:
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod3()) # corrente de saída lida pelo bastidor testado
                    self.FBP.SetSlaveAdd(5) # jiga bastidor
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod3()) # corrente de saída lida pela jiga bastidor

                elif modulo == 3:
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod4()) # corrente de saída lida pelo bastidor testado
                    self.FBP.SetSlaveAdd(5) # jiga bastidor
                    MeasCurr[modulo][0].append(self.FBP.Read_iMod4()) # corrente de saída lida pela jiga bastidor

                time.sleep(1)
                self.FBP.SetSlaveAdd(1) # bastidor em teste
                self.FBP.ConfigWfmRef(modulo+1, 0) # ajusta 0% do ciclo de trabalho apenas para o modulo testado
                self.FBP.WfmRefUpdate()

            for modulo in range(4):
                self.FBP.ConfigWfmRef(modulo+1, -20) # ajusta -20% do ciclo de trabalho apenas para o modulo testado
                self.FBP.WfmRefUpdate()

                time.sleep(5)
                MeasCurr[modulo][1].append(self.FBP.Read_iMod1()) # corrente de saída lida pelo bastidor testado
                self.FBP.SetSlaveAdd(5) # jiga bastidor
                MeasCurr[modulo][1].append(self.FBP.Read_iMod1()) # corrente de saída liga pela jiga bastidor

                time.sleep(1)
                self.FBP.SetSlaveAdd(1) # bastidor em teste
                self.FBP.ConfigWfmRef(modulo+1, 0) # ajusta 0% do ciclo de trabalho apenas para o modulo testado
                self.FBP.WfmRefUpdate()


            #TODO: Sequencia de Testes
            """
            Simulação de valores
            """
            log = PowerSupplyLog()
            log.id_canal_power_supply = 1
            log.test_result = "Aprovado"
            log.result_test_on_off = "Aprovado"
            log.serial_number_power_supply = self._serial_number
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

    

    def _read_SoftInterlock(self, int_interlock):
        SoftInterlockList = ['N/A', 'Sobre-tensão na carga 1', 'N/A', \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensão na carga 2', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensão na carga 3', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensão na carga 4', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        op_bin = 1
        ActiveSoftInterlocks = []

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveSoftInterlocks.append(SoftInterlockList[i])

        return ActiveSoftInterlocks

    def _read_HardInterlock(self, int_interlock):
        HardInterlockList = ['Sobre-corrente na carga 1', 'N/A',                   \
                             'Sobre-tensão no DC-Link do módulo 1',                \
                             'Sub-tensão no DC-Link do módulo 1',                  \
                             'Falha no relé de entrada do DC-Link do módulo 1',    \
                             'Falha no fusível de entrada do DC-Link do módulo 1', \
                             'Falha nos drivers do módulo 1',                      \
                             'Sobre-temperatura no módulo 1',                      \
                             'Sobre-corrente na carga 2', 'N/A',                   \
                             'Sobre-tensão no DC-Link do módulo 2',                \
                             'Sub-tensão no DC-Link do módulo 2',                  \
                             'Falha no relé de entrada do DC-Link do módulo 2',    \
                             'Falha no fusível de entrada do DC-Link do módulo 2', \
                             'Falha nos drivers do módulo 2',                      \
                             'Sobre-temperatura no módulo 2',                      \
                             'Sobre-corrente na carga 3', 'N\A',                   \
                             'Sobre-tensão no DC-Link do módulo 3',                \
                             'Sub-tensão no DC-Link do módulo 3',                  \
                             'Falha no relé de entrada no DC-Link do módulo 3',    \
                             'Falha no fusível de entrada do DC-Link do módulo 3', \
                             'Falha nos drivers do módulo 3',                      \
                             'Sobre-temperatura no módulo 3',                      \
                             'Sobre-corrente na carga 4', 'N/A',                   \
                             'Sobre-tensão no DC-Link do módulo 4',                \
                             'Sub-tensão no DC-Link do módulo 4',                  \
                             'Falha no relé de entrada do DC-Link do módulo 4',    \
                             'Falha no fusível de entrada do DC-Link do módulo 4', \
                             'Falha nos drivers do módulo 4',                      \
                             'Sobre-temperatura no módulo 4']
        op_bin = 1
        ActiveHardInterlocks = []

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveHardInterlocks.append(HardInterlockList[i])

        return ActiveHardInterlocks

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

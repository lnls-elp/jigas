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
    current_state       = pyqtSignal(str)
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
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self, ps_address):
        result = False
        self.FBP.SetSlaveAdd(ps_address)
        time.sleep(1)

        try:
            self.FBP.Config_nHRADC(4) # alterar para 4
            # self.FBP.Write_sigGen_Aux(1) # alterar para 4
            time.sleep(1)
            test_package = self.FBP.Read_ps_Model()
            time.sleep(1)

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
        time.sleep(0.5)

        self.FBP.SetSlaveAdd(ps_address)
        time.sleep(0.5)

        if self.test_communication(ps_address):
            self.FBP.SetRSAddress(self._ps_address)
            time.sleep(1)

            if self.test_communication(self._ps_address):
                write_gui.append(str(self._ps_address))
                write_gui.append('endereço ' + str(self._ps_address) + ' gravado com sucesso')
                print('endereço ' + str(self._ps_address) + ' gravado com sucesso')
                self._ps_address = self._ps_address + 1
            else:
                write_gui.append('erro na gravação do endereço')
                print('erro na gravação do endereço')

        return write_gui

    def _test_sequence(self):
        self.current_state.emit('Desligado')

        print('##################################################')
        print('##################################################')
        print(self._serial_number)
        print('##################################################')
        print('##################################################')

        # for set_current in [10, -10]:
        for set_current in [7, -7]: # alterar para 10 e -10, adequação à carga da WEG
            for ps_turnOn in self._serial_number:
                if self.test_communication(self._serial_number.index(ps_turnOn) + 1):
                    self.update_gui.emit('Ligando fontes e setando correntes para ' \
                                         + str(set_current) + ' A')
                    self.FBP.SetSlaveAdd(self._serial_number.index(ps_turnOn) + 1)
                    self.FBP.Config_nHRADC(4)# alterar para 4
                    # self.FBP.Write_sigGen_Aux(1) # alterar para 4
                    time.sleep(1)
                    #REMOVER----------------------------------------------------
                    '''
                    for b in range(4):
                        print('config dp ' + str(b))
                        self.FBP.Write_dp_Class(3)#REMOVER
                        time.sleep(1)
                        self.FBP.Write_dp_ID(b)#REMOVER
                        time.sleep(1)
                        self.FBP.Write_dp_Coeffs([1.9, 559])#REMOVER
                        time.sleep(1)
                        self.FBP.ConfigDPModule()#REMOVER
                        time.sleep(1)
                    '''
                    #REMOVER----------------------------------------------------
                    self.FBP.ResetInterlocks()
                    time.sleep(0.5)
                    self.FBP.TurnOn(0b1111)#alterar para 0b1111
                    time.sleep(1)
                    self.FBP.ClosedLoop(0b1111)#alterar para 0b1111
                    time.sleep(1)
                    self.FBP.SetISlowRef(set_current)
                    time.sleep(0.5)
                    self.current_state.emit(str(set_current) + 'A')

                else:
                    self.update_gui.emit('Endereço não encontrado')
                    print('Endereço não encontrado')

            for a in range(72): #alterar para 72
                for ps_under_test in self._serial_number:
                    result = True
                    ps = PowerSupply()
                    ps.serial_number = ps_under_test
                    res = self._send_to_server(ps)
                    self.update_gui.emit('Medição da fonte de número serial '\
                                         + str(ps_under_test))
                    self.update_gui.emit('')

                    if self.test_communication(self._serial_number.index(ps_under_test) + 1):
                        if res:
                            #TODO: Sequencia de Testes

                            for i in range(4):# Alterar para 4
                                self.update_gui.emit('Iniciando medições do módulo ' + str(i + 1))
                                self.update_gui.emit('')
                                test = True
                                MeasureList = self._save_AllMeasurements\
                                (self._serial_number.index(ps_under_test) + 1, i)

                                '''########## Verificando resultado da corrente de saída ##########'''
                                '''################################################################'''
                                self.update_gui.emit('          Corrente de saída: ' + str(MeasureList[0]))
                                if round(MeasureList[0]) == set_current:
                                    self.update_gui.emit('          Leitura da corrente de saída OK')
                                    if test:
                                        test = True
                                else:
                                    test = False
                                    self.update_gui.emit('          Leitura da corrente de saída NOK')
                                self.update_gui.emit('')
                                '''################################################################'''


                                '''########### Verificando resultado da tensão de saída ###########'''
                                '''################################################################'''
                                self.update_gui.emit('          Tensão de saída: ' + str(MeasureList[1]))
                                if set_current == 7:
                                    if 2 <= round(MeasureList[1]) <= 5:
                                        self.update_gui.emit('          Leitura da tensão de saída OK')
                                        if test:
                                            test = True
                                    else:
                                        test = False
                                        self.update_gui.emit('          Leitura da tensão de saída NOK')

                                elif set_current == -7:
                                    if -5 <= round(MeasureList[1]) <= -2:
                                        self.update_gui.emit('          Leitura da tensão de saída OK')
                                        if test:
                                            test = True
                                    else:
                                        test = False
                                        self.update_gui.emit('          Leitura da tensão de saída NOK')
                                self.update_gui.emit('')
                                '''################################################################'''


                                '''########## Verificando resultado da tensão de entrada ##########'''
                                '''################################################################'''
                                self.update_gui.emit('          Tensão de entrada: ' + str(MeasureList[2]))
                                if 5 <= round(MeasureList[2]) <= 7:
                                    self.update_gui.emit('          Leitura da tensão de entrada OK')
                                    if test:
                                        test = True
                                else:
                                    test = False
                                    self.update_gui.emit('          Leitura da tensão de entrada NOK')
                                self.update_gui.emit('')
                                '''################################################################'''


                                '''############# Verificando resultado da temperatura #############'''
                                '''################################################################'''
                                self.update_gui.emit('          Temperatura: ' + str(MeasureList[3]))
                                if round(MeasureList[3]) < 90:
                                    self.update_gui.emit('          Leitura da temperatura OK')
                                    if test:
                                        test = True
                                else:
                                    test = False
                                    self.update_gui.emit('          Leitura da temperatura NOK')
                                self.update_gui.emit('')
                                '''################################################################'''

                                if set_current == 7:
                                    log = PowerSupplyLog()
                                    log.test_type = self.test['Burn-In']
                                    log.id_canal_power_supply = i + 1
                                    if test:
                                        log.test_result = 'Aprovado'
                                        self.update_gui.emit('          MÓDULO ' + str(i + 1) + ' OK')
                                        self.update_gui.emit('')
                                    else:
                                        log.test_result = 'Reprovado'
                                        self.update_gui.emit('          MÓDULO ' + str(i + 1) + ' NOK')
                                        self.update_gui.emit('')
                                    log.serial_number_power_supply = ps_under_test
                                    log.iout0 = MeasureList[0]
                                    log.vout0 = MeasureList[1]
                                    log.vdclink0 = MeasureList[2]
                                    log.temperatura0 = MeasureList[3]

                                    log.details = ''

                                    for _softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
                                        log.details = log.details + _softinterlock + '\t'

                                    for _hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
                                        log.details = log.details + _hardinterlock + '\t'

                                    result = self._send_to_server(log)

                                elif set_current == -7:
                                    log = PowerSupplyLog()
                                    log.test_type = self.test['Burn-In']
                                    log.id_canal_power_supply = i + 1
                                    if test:
                                        log.test_result = 'Aprovado'
                                    else:
                                        log.test_result = 'Reprovado'
                                    log.serial_number_power_supply = ps_under_test
                                    log.iout1 = MeasureList[0]
                                    log.vout1 = MeasureList[1]
                                    log.vdclink1 = MeasureList[2]
                                    log.temperatura1 = MeasureList[3]

                                    log.details = ''

                                    for _softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
                                        log.details = log.details + _softinterlock + '\t'

                                    for _hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
                                        log.details = log.details + _hardinterlock + '\t'

                                    result = self._send_to_server(log)

                            self.update_gui.emit('          Interlocks Ativos:')
                            for softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
                                self.update_gui.emit('          ' + softinterlock)
                            for hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
                                self.update_gui.emit('          ' + hardinterlock)
                            self.update_gui.emit('')
                            self.update_gui.emit('*********************************************************')
                    else:
                        self.update_gui.emit('Endereço não encontrado')
                        print('Endereço não encontrado')
                if test:
                    if result:
                        result = True
                else:
                    result = False

                time.sleep(600) #Alterar para 600

        self.test_complete.emit(result)
        self.update_gui.emit('FIM DO TESTE!')
        self.FBP.TurnOff(0b1111)

    def _save_AllMeasurements(self, address, module):
        self.FBP.SetSlaveAdd(address)
        Measurement = []

        if module == 0:
            Measurement.append(self.FBP.Read_iMod1())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vOutMod1())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vDCMod1())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_temp1())
            time.sleep(0.1)

        elif module == 1:
            Measurement.append(self.FBP.Read_iMod2())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vOutMod2())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vDCMod2())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_temp2())
            time.sleep(0.1)

        elif module == 2:
            Measurement.append(self.FBP.Read_iMod3())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vOutMod3())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vDCMod3())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_temp3())
            time.sleep(0.1)

        elif module == 3:
            Measurement.append(self.FBP.Read_iMod4())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vOutMod4())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_vDCMod4())
            time.sleep(0.1)
            Measurement.append(self.FBP.Read_temp4())
            time.sleep(0.1)

        return Measurement

    def _read_SoftInterlock(self, int_interlock):
        SoftInterlockList = ['N/A', 'Sobre-tensao na carga 1', 'N/A', \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 2', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 3', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 4', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        op_bin = 1
        ActiveSoftInterlocks = []

        print('Soft Interlocks ativos:')

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveSoftInterlocks.append(SoftInterlockList[i])
                print(SoftInterlockList[i])
        print('-------------------------------------------------------------------')

        return ActiveSoftInterlocks

    def _read_HardInterlock(self, int_interlock):
        HardInterlockList = ['Sobre-corrente na carga 1', 'N/A',                   \
                             'Sobre-tensao no DC-Link do modulo 1',                \
                             'Sub-tensao no DC-Link do modulo 1',                  \
                             'Falha no rele de entrada do DC-Link do modulo 1',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 1', \
                             'Falha nos drivers do modulo 1',                      \
                             'Sobre-temperatura no modulo 1',                      \
                             'Sobre-corrente na carga 2', 'N/A',                   \
                             'Sobre-tensao no DC-Link do modulo 2',                \
                             'Sub-tensao no DC-Link do modulo 2',                  \
                             'Falha no rele de entrada do DC-Link do modulo 2',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 2', \
                             'Falha nos drivers do modulo 2',                      \
                             'Sobre-temperatura no modulo 2',                      \
                             'Sobre-corrente na carga 3', 'N\A',                   \
                             'Sobre-tensao no DC-Link do modulo 3',                \
                             'Sub-tensao no DC-Link do modulo 3',                  \
                             'Falha no rele de entrada no DC-Link do modulo 3',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 3', \
                             'Falha nos drivers do modulo 3',                      \
                             'Sobre-temperatura no modulo 3',                      \
                             'Sobre-corrente na carga 4', 'N/A',                   \
                             'Sobre-tensao no DC-Link do modulo 4',                \
                             'Sub-tensao no DC-Link do modulo 4',                  \
                             'Falha no rele de entrada do DC-Link do modulo 4',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 4', \
                             'Falha nos drivers do modulo 4',                      \
                             'Sobre-temperatura no modulo 4']
        op_bin = 1
        ActiveHardInterlocks = []

        print('Hard Interlocks ativos:')

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveHardInterlocks.append(HardInterlockList[i])
                print(HardInterlockList[i])
        print('-------------------------------------------------------------------')

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

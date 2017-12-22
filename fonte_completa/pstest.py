from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.psdata import PowerSupply, PowerSupplyLog
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
            return self.FBP.Connect(self._comport, self._baudrate)

    def test_communication(self):
        result = (False, False) # Result for communication test and aux power supply
        test = []
        #TODO: Communication test

        for i in range(2):
            try:
                if i == 0:
                    print('Configurando UDC da Fonte...')
                    self.FBP.SetSlaveAdd(1)      # Endereço do controlador
                    self.FBP.Config_nHRADC(4)
                elif i == 1:
                    print('Configurando UDC da jiga...')
                    self.FBP.SetSlaveAdd(5)      # Endereço do controlador
                    self.FBP.Write_sigGen_Aux(0) # Usando 4 fontes no bastidor
                                                 # em teste e 0 na jiga bastidor

                time.sleep(1)
                test_package = self.FBP.Read_ps_Model()

                if (test_package[0] == 0)   and (test_package[1] == 17) and \
                   (test_package[2] == 512) and (test_package[3] == 14) and \
                   (test_package[4] == 223):
                    test.append(True)
                else:
                    test.append(False)
            except:
                print('ERRO!!!')
                test.append(False)

        if test == [True, True]:
            result = (True, True)
        else:
            result = (False, False)
        return result

    def _test_sequence(self):
        result = True
        send_to_server_result = False
        OnOff  = ['Reprovado' for i in range(4)]
        MeasDCLink = [[]  for j in range(4)]
        MeasVout   = [[]  for k in range(4)]
        MeasTemp   = [[]  for l in range(4)]
        MeasCurr   = [[[] for m in range(5)] for n in range(4)]
        compare_current = [3, -3, 5, 10, -10]

        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        ps = PowerSupply()
        ps.serial_number = self._serial_number
        res = self._send_to_server(ps)

        if res:
            self.FBP.SetSlaveAdd(1) # Bastidor em teste
            time.sleep(1)
            self.FBP.ResetInterlocks()
            time.sleep(5)
            # self.FBP.TurnOff(0b1111)
            # time.sleep(5)

            '''########################### Teste Liga/Desliga ###########################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste liga/desliga dos módulos de potência...')
            for module in range(4):
                self.FBP.TurnOn(2**module)
                time.sleep(1)
                # self.FBP.OpenLoop(2**module)
                # time.sleep(1)

                if self.FBP.Read_ps_OnOff() == 2 ** module:
                    OnOff[module] = 'OK'
                else:
                    self.update_gui.emit('O módulo ' + str(module + 1) + ' não ligou corretamente')
                    OnOff[module] = 'NOK'
                time.sleep(1)

                self.FBP.TurnOff(2**module)

                if self.FBP.Read_ps_OnOff() == 0:
                    if OnOff[module] == 'OK':
                        OnOff[module] = 'OK'
                else:
                    OnOff[module] = 'NOK'
                    self.update_gui.emit('O módulo ' + str(module + 1) + ' não desligou corretamente')
                time.sleep(1)
            '''##########################################################################'''

            self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks())
            self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks())

            self.FBP.TurnOn(0b1111)   # liga todos os módulos
            time.sleep(5)
            self.FBP.OpenLoop(0b1111) # todos os módulos em malha aberta
            #self.FBP.OpMode(2)        # coloca a fonte no modo WfmRef para setar as correntes individualmente

            '''#################### Teste em Malha Aberta com 20% #######################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste com módulos em malha aberta a 20%...')
            for module in range(4):
                if module == 0:
                    self.FBP.SetISlowRefx4(20, 0, 0, 0)
                elif module == 1:
                    self.FBP.SetISlowRefx4(0, 20, 0, 0)
                elif module == 2:
                    self.FBP.SetISlowRefx4(0, 0, 20, 0)
                elif module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, 20)

                time.sleep(2)

                MeasureList = self._save_CurrentMeasurement(module)

                for current in MeasureList:
                    MeasCurr[module][0].append(current)

                time.sleep(1)
                self.FBP.SetSlaveAdd(1) # bastidor em teste

                print('mod1: ' + str(self.FBP.Read_iMod1()))
                time.sleep(0.1)
                print('mod2: ' + str(self.FBP.Read_iMod2()))
                time.sleep(0.1)
                print('mod3: ' + str(self.FBP.Read_iMod3()))
                time.sleep(0.1)
                print('mod4: ' + str(self.FBP.Read_iMod4()) + '\n')
                time.sleep(0.1)

                #self.FBP.ConfigWfmRef(module+1, 0) # ajusta 0 o ciclo de trabalho apenas para o modulo testado
                if module == 0 or module == 1 or module == 2 or module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, 0)

                time.sleep(2)
            '''##########################################################################'''

            self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks())
            self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks())

            '''#################### Teste em Malha Aberta com -20% ######################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste com módulos em malha aberta a -20%...')
            for module in range(4):
                if module == 0:
                    self.FBP.SetISlowRefx4(-20, 0, 0, 0)
                elif module == 1:
                    self.FBP.SetISlowRefx4(0, -20, 0, 0)
                elif module == 2:
                    self.FBP.SetISlowRefx4(0, 0, -20, 0)
                elif module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, -20)
                time.sleep(2)

                MeasureList = self._save_CurrentMeasurement(module)

                for current in MeasureList:
                    MeasCurr[module][1].append(current)

                time.sleep(1)
                self.FBP.SetSlaveAdd(1) # bastidor em teste

                print('mod1: ' + str(self.FBP.Read_iMod1()))
                time.sleep(0.1)
                print('mod2: ' + str(self.FBP.Read_iMod2()))
                time.sleep(0.1)
                print('mod3: ' + str(self.FBP.Read_iMod3()))
                time.sleep(0.1)
                print('mod4: ' + str(self.FBP.Read_iMod4()) + '\n')
                time.sleep(0.1)

                if module == 0 or module == 1 or module == 2 or module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, 0)
                time.sleep(2)
            '''##########################################################################'''

            self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks())
            self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks())

            '''#################### Teste em Malha Fechada com 5A #######################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste com módulos em malha fechada a 5A...')

            for module in range(4):
                self.FBP.ClosedLoop(2**module)
                time.sleep(1)
                if module == 0:
                    self.FBP.SetISlowRefx4(5, 0, 0, 0)
                elif module == 1:
                    self.FBP.SetISlowRefx4(0, 5, 0, 0)
                elif module == 2:
                    self.FBP.SetISlowRefx4(0, 0, 5, 0)
                elif module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, 5)
                time.sleep(2)

                MeasureList = self._save_CurrentMeasurement(module)

                print('mod1: ' + str(self.FBP.Read_iMod1()))
                time.sleep(0.1)
                print('mod2: ' + str(self.FBP.Read_iMod2()))
                time.sleep(0.1)
                print('mod3: ' + str(self.FBP.Read_iMod3()))
                time.sleep(0.1)
                print('mod4: ' + str(self.FBP.Read_iMod4()) + '\n')
                time.sleep(0.1)

                for current in MeasureList:
                    MeasCurr[module][2].append(current)

                self.FBP.SetSlaveAdd(1)

                if module == 0 or module == 1 or module == 2 or module == 3:
                    self.FBP.SetISlowRefx4(0, 0, 0, 0)
                time.sleep(2)
                self.FBP.OpenLoop(2**module)
                time.sleep(2)
            '''##########################################################################'''

            self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks())
            self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks())

            '''################### Teste em Malha Fechada com 10A #######################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste com módulos em malha fechada a 10A...')
            self.FBP.ClosedLoop(0b1111)
            time.sleep(2)
            self.FBP.OpMode(0)
            time.sleep(2)
            self.FBP.SetISlowRefx4(10, 10, 10, 10)
            time.sleep(1)

            for module in range(4):
                time.sleep(5)
                MeasureList = self._save_CurrentMeasurement(module)
                for current in MeasureList:
                    MeasCurr[module][3].append(current)

            self.FBP.SetSlaveAdd(1)

            print('mod1: ' + str(self.FBP.Read_iMod1()))
            time.sleep(0.1)
            print('mod2: ' + str(self.FBP.Read_iMod2()))
            time.sleep(0.1)
            print('mod3: ' + str(self.FBP.Read_iMod3()))
            time.sleep(0.1)
            print('mod4: ' + str(self.FBP.Read_iMod4()) + '\n')
            time.sleep(0.1)
            '''##########################################################################'''

            print('Interlocks Ativos: ')
            for softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
                if softinterlock == None:
                    print('None')
                else:
                    print(softinterlock)
            for hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
                if hardinterlock == None:
                    print('None')
                else:
                    print(hardinterlock)
            print('--------------------------------------------\n')

            self.update_gui.emit('Realizando medidas de tensão do DC-Link, tensão de saída e temperatura')
            for o in range(8):
                time.sleep(30)#Alterar tempo
                MeasDCLink[0].append(self.FBP.Read_vDCMod1())
                time.sleep(0.1)
                MeasDCLink[1].append(self.FBP.Read_vDCMod2())
                time.sleep(0.1)
                MeasDCLink[2].append(self.FBP.Read_vDCMod3())
                time.sleep(0.1)
                MeasDCLink[3].append(self.FBP.Read_vDCMod4())
                time.sleep(0.1)

                MeasVout[0].append(self.FBP.Read_vOutMod1())
                time.sleep(0.1)
                MeasVout[1].append(self.FBP.Read_vOutMod2())
                time.sleep(0.1)
                MeasVout[2].append(self.FBP.Read_vOutMod3())
                time.sleep(0.1)
                MeasVout[3].append(self.FBP.Read_vOutMod4())
                time.sleep(0.1)

                MeasTemp[0].append(self.FBP.Read_temp1())
                time.sleep(0.1)
                MeasTemp[1].append(self.FBP.Read_temp2())
                time.sleep(0.1)
                MeasTemp[2].append(self.FBP.Read_temp3())
                time.sleep(0.1)
                MeasTemp[3].append(self.FBP.Read_temp4())
                time.sleep(0.1)

            self.FBP.SetSlaveAdd(1)
            '''################### Teste em Malha Fechada com -10A ######################'''
            '''##########################################################################'''
            self.update_gui.emit('Iniciando teste com módulos em malha fechada a -10A...')
            self.FBP.SetISlowRefx4(0, 0, 0, 0)
            time.sleep(0.5)
            self.FBP.SetISlowRefx4(-10, -10, -10, -10)

            for module in range(4):
                time.sleep(5)
                MeasureList = self._save_CurrentMeasurement(module)
                for current in MeasureList:
                    MeasCurr[module][4].append(current)

            self.FBP.SetSlaveAdd(1)

            print('mod1: ' + str(self.FBP.Read_iMod1()))
            time.sleep(0.1)
            print('mod2: ' + str(self.FBP.Read_iMod2()))
            time.sleep(0.1)
            print('mod3: ' + str(self.FBP.Read_iMod3()))
            time.sleep(0.1)
            print('mod4: ' + str(self.FBP.Read_iMod4()) + '\n')
            time.sleep(0.1)
            '''##########################################################################'''

            print('Interlocks Ativos: ')
            for softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
                if softinterlock == None:
                    print('None')
                else:
                    print(softinterlock)
            for hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
                if hardinterlock == None:
                    print('None')
                else:
                    print(hardinterlock)
            print('--------------------------------------------\n')

            self.update_gui.emit('Realizando medidas de tensão do DC-Link, tensão de saída e temperatura')
            for p in range(8):
                time.sleep(30)# alterar tempo
                MeasDCLink[0].append(self.FBP.Read_vDCMod1())
                time.sleep(0.1)
                MeasDCLink[1].append(self.FBP.Read_vDCMod2())
                time.sleep(0.1)
                MeasDCLink[2].append(self.FBP.Read_vDCMod3())
                time.sleep(0.1)
                MeasDCLink[3].append(self.FBP.Read_vDCMod4())
                time.sleep(0.1)

                MeasVout[0].append(self.FBP.Read_vOutMod1())
                time.sleep(0.1)
                MeasVout[1].append(self.FBP.Read_vOutMod2())
                time.sleep(0.1)
                MeasVout[2].append(self.FBP.Read_vOutMod3())
                time.sleep(0.1)
                MeasVout[3].append(self.FBP.Read_vOutMod4())
                time.sleep(0.1)

                MeasTemp[0].append(self.FBP.Read_temp1())
                time.sleep(0.1)
                MeasTemp[1].append(self.FBP.Read_temp2())
                time.sleep(0.1)
                MeasTemp[2].append(self.FBP.Read_temp3())
                time.sleep(0.1)
                MeasTemp[3].append(self.FBP.Read_temp4())
                time.sleep(0.1)

            self.FBP.SetSlaveAdd(1)

            self.FBP.SetISlowRefx4(0, 0, 0, 0)
            time.sleep(1)
            self.FBP.TurnOff(0b1111)

            for module in range(4):
                log = PowerSupplyLog()
                log.id_canal_power_supply = module + 1

                test = [True for p in range(9)]
                n = 0

                self.update_gui.emit('')
                self.update_gui.emit('Verificando resultados do módulo '\
                                     + str(module + 1) + '...')
                '''-------------------------------------------------------------'''
                for a in compare_current:
                    for b in MeasCurr[module][n]:
                        if a == round(b):
                            if test[n]:
                                test[n] = True
                        else:
                            test[n] = False
                    if test[n]:
                        self.update_gui.emit('      Aprovado no teste ' + str(compare_current.index(a) + 1) + ' de corrente de saída')
                    else:
                        self.update_gui.emit('      Reprovado no teste ' + str(compare_current.index(a) + 1) + ' de corrente de saída')
                    n = n + 1
                '''-------------------------------------------------------------'''

                '''-------------------------------------------------------------'''
                for c in MeasDCLink[module]:
                    if (14 <= round(c)) and (round(c) <= 16):
                        if test[5]:
                            test[5] = True
                    else:
                        test[5] = False
                if test[5]:
                    self.update_gui.emit('      Aprovado no teste de leitura da tensão do DC Link')
                else:
                    self.update_gui.emit('      Reprovado no teste de leitura da tensão do DC Link')
                '''-------------------------------------------------------------'''

                '''-------------------------------------------------------------'''
                for d in MeasTemp[module]:
                    if d < 90:
                        if test[6]:
                            test[6] = True
                    else:
                        test[6] = False
                if test[6]:
                    self.update_gui.emit('      Aprovado no teste de leitura da temperatura')
                else:
                    self.update_gui.emit('      Reprovado no teste de leitura da temperatura')
                '''-------------------------------------------------------------'''

                '''-------------------------------------------------------------'''
                for e in range(0, len(MeasVout) - 8):
                    if 10 < MeasVout[module][e] < 12:
                        if test[7]:
                            test[7] = True
                    else:
                        test[7] = False
                if test[7]:
                    self.update_gui.emit('      Aprovado no teste 1 de leitura da tensão de saída')
                else:
                    self.update_gui.emit('      Reprovado no teste 1 de leitura da tensão de saída')
                '''-------------------------------------------------------------'''

                '''-------------------------------------------------------------'''
                for f in range(8, len(MeasVout)):
                    if -12 < MeasVout[module][f] < -10:
                        if test[8]:
                            test[8] = True
                    else:
                        test[8] = False
                if test[8]:
                    self.update_gui.emit('      Aprovado no teste 2 de leitura da tensão de saída')
                else:
                    self.update_gui.emit('      Reprovado no teste 2 de leitura da tensão de saída')
                '''-------------------------------------------------------------'''

                if test == [True for g in range(9)]:
                    if result:
                        result = True
                    log.test_result = 'Aprovado'
                else:
                    log.test_result = 'Reprovado'
                    result = False

                log.result_test_on_off = OnOff[module]
                log.serial_number_power_supply = self._serial_number
                log.iout0                   = MeasCurr[module][3][0]
                log.iout1                   = MeasCurr[module][4][0]
                log.vout0                   = MeasVout[module][7]
                log.vout1                   = MeasVout[module][15]
                log.vdclink0                = MeasDCLink[module][7]
                log.vdclink1                = MeasDCLink[module][15]
                log.temperatura0            = MeasTemp[module][7]
                log.temperatura1            = MeasTemp[module][15]
                log.iout_add_20_duty_cycle  = MeasCurr[module][0][0]
                log.iout_less_20_duty_cycle = MeasCurr[module][1][0]
                log.details = ''

                send_to_server_result = self._send_to_server(log)

        self.update_gui.emit('')
        self.update_gui.emit('Interlocks Ativos:')
        for softinterlock in self._read_SoftInterlock(self.FBP.Read_ps_SoftInterlocks()):
            self.update_gui.emit(softinterlock)
        for hardinterlock in self._read_HardInterlock(self.FBP.Read_ps_HardInterlocks()):
            self.update_gui.emit(hardinterlock)
        print('--------------------------------------------\n')

        self.test_complete.emit(result)

    def _save_CurrentMeasurement(self, module):

        Measurement = []

        if module == 0:
            self.FBP.SetSlaveAdd(1) # bastidor em teste
            Measurement.append(self.FBP.Read_iMod1()) # corrente de saída lida pelo bastidor testado
            time.sleep(0.1)
            self.FBP.SetSlaveAdd(5) # jiga bastidor
            Measurement.append(self.FBP.Read_iMod1()) # corrente de saída lida pela jiga bastidor
            time.sleep(0.1)

        elif module == 1:
            self.FBP.SetSlaveAdd(1) # bastidor em teste
            Measurement.append(self.FBP.Read_iMod2()) # corrente de saída lida pelo bastidor testado
            time.sleep(0.1)
            self.FBP.SetSlaveAdd(5) # jiga bastidor
            Measurement.append(self.FBP.Read_iMod2()) # corrente de saída lida pela jiga bastidor
            time.sleep(0.1)

        elif module == 2:
            self.FBP.SetSlaveAdd(1) # bastidor em teste
            Measurement.append(self.FBP.Read_iMod3()) # corrente de saída lida pelo bastidor testado
            time.sleep(0.1)
            self.FBP.SetSlaveAdd(5) # jiga bastidor
            Measurement.append(self.FBP.Read_iMod3()) # corrente de saída lida pela jiga bastidor
            time.sleep(0.1)

        elif module == 3:
            self.FBP.SetSlaveAdd(1) # bastidor em teste
            Measurement.append(self.FBP.Read_iMod4()) # corrente de saída lida pelo bastidor testado
            time.sleep(0.1)
            self.FBP.SetSlaveAdd(5) # jiga bastidor
            Measurement.append(self.FBP.Read_iMod4()) # corrente de saída lida pela jiga bastidor
            time.sleep(0.1)

        return Measurement

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

        print('Soft Interlocks ativos:')

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveSoftInterlocks.append(SoftInterlockList[i])
                print(SoftInterlockList[i])
        print('-------------------------------------------------------------------')

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
        print(client_data)
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        print(client_response)
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

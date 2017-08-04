from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from pmdata import PowerModule, PowerModuleLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
import serial
import random
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
        self.FBP = SerialDRS()


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

            if (test_package[0] == 0)   and \
               (test_package[1] == 17)  and \
               (test_package[2] == 512) and \
               (test_package[3] == 14)  and \
               (test_package[4] == 223):
               result = ['OK', 'OK', 'OK', 'OK']

            else:
                result = ['Falha', 'Falha', 'Falha', 'Falha']
        except:
            result = ['Falha', 'Falha', 'Falha', 'Falha']

        return result

    def _test_sequence(self):
        response = [None for i in range(4)]

        serial = [self._serial_mod0, self._serial_mod1, self._serial_mod2,
                    self._serial_mod3]

        mod_result1      = [[] for j in range(4)] # para medidas de iout
        mod_result2      = [[] for k in range(4)] # para medidas de vout
        mod_result3      = [[] for l in range(4)] # para medidas de temperatura
        mod_result4      = [[] for m in range(4)] # para medidas de dclink
        load_current     = ['turnedOff', 0, 5, 10, -10, -5] # correntes setadas
        compare_current  = [0, 0, 5, 10, -10, -5] # para comparar medidas de correntes

        if not self._serial_port.is_open:
            self.connection_lost.emit()
            #TODO: Encerra testes

        '''###########################################################'''
        '''Número de módulos conectados para inicializar o controlador'''
        '''###########################################################'''
        n_mod = 0
        for o in range(0, len(serial)):
            if serial[o] != None:
                n_mod = n_mod+1
        self.FBP.Write_sigGen_Aux(n_mod)
        '''###########################################################'''
        '''###########################################################'''


        '''###############################################################################'''
        '''Setando todos os valores de corrente e salvando resultados na matriz mod_result'''
        '''###############################################################################'''

        for set_current in load_current:
            if set_current == 'turnedOff':
                self.FBP.TurnOff()
                self.update_gui.emit('Iniciando medições com módulos desligados')
                time.sleep(2) # Alterar para 2 min
            else:
                self.FBP.TurnOn()
                self.FBP.ClosedLoop()
                time.sleep(0.5)
                self.update_gui.emit('Iniciando medições com módulos ligados a '\
                                    + str(set_current) + 'A')
                self.FBP.SetISlowRef(0.25 * set_current)
                time.sleep(0.5)
                self.FBP.SetISlowRef(0.5 * set_current)
                time.sleep(0.5)
                self.FBP.SetISlowRef(set_current)
                time.sleep(5) # Alterar para 2 min

            if serial[0] != None:
                mod_result1[0].append(self.FBP.Read_iMod1())
                mod_result2[0].append(self.FBP.Read_vOutMod1())
                mod_result3[0].append(self.FBP.Read_temp1())
                mod_result4[0].append(self.FBP.Read_vDCMod1())

            if serial[1] != None:
                mod_result1[1].append(self.FBP.Read_iMod2())
                mod_result2[1].append(self.FBP.Read_vOutMod2())
                mod_result3[1].append(self.FBP.Read_temp2())
                mod_result4[1].append(self.FBP.Read_vDCMod2())

            if serial[2] != None:
                mod_result1[2].append(self.FBP.Read_iMod3())
                mod_result2[2].append(self.FBP.Read_vOutMod3())
                mod_result3[2].append(self.FBP.Read_temp3())
                mod_result4[2].append(self.FBP.Read_vDCMod3())

            if serial[3] != None:
                mod_result1[3].append(self.FBP.Read_iMod4())
                mod_result2[3].append(self.FBP.Read_vOutMod4())
                mod_result3[3].append(self.FBP.Read_temp4())
                mod_result4[3].append(self.FBP.Read_vDCMod4())

        self.FBP.TurnOff()
        '''###############################################################################'''
        '''###############################################################################'''

        for item in serial:
            if item is not None:

                power_module = PowerModule()
                power_module.serial_number = item
                #res = self._send_to_server(power_module)

                test = [True for p in range(4)]

                if True:#res:
                    self.update_gui.emit('')
                    self.update_gui.emit('Verificando resultados do módulo '\
                                        + str(serial.index(item)+1) + '...')
                    log = PowerModuleLog()
                    log.serial_number_power_module = item

                    # TODO: Faz os testes e seta os atributos de log
                    for q in range(0, len(mod_result1[serial.index(item)])):
                        if round(mod_result1[serial.index(item)][q]) == \
                           compare_current[q]:
                            if test[0]:
                                test[0] = True
                        else:
                            test[0] = False
                    if test[0]:
                        self.update_gui.emit('      Aprovado no teste de corrente de saída')
                    else:
                        self.update_gui.emit('      Reprovado no teste de corrente de saída')

                    if round(mod_result2[serial.index(item)][0]) == 0     and \
                       round(mod_result2[serial.index(item)][1]) == 0     and \
                             3 < mod_result2[serial.index(item)][2] < 4   and \
                             7 < mod_result2[serial.index(item)][3] < 8   and \
                             -8 < mod_result2[serial.index(item)][4] < -7 and \
                             -4 < mod_result2[serial.index(item)][5] < -3:
                        test[1] = True
                    else:
                        test[1] = False
                    if test[1]:
                        self.update_gui.emit('      Aprovado no teste de tensão de saída')
                    else:
                        self.update_gui.emit('      Reprovado no teste de tensão de saída')

                    for r in range(0, len(mod_result3[serial.index(item)])):
                        if mod_result3[serial.index(item)][r] < 90:
                            if test[2]:
                                test[2] = True
                        else:
                            test[2] = False
                    if test[2]:
                        self.update_gui.emit('      Aprovado no teste de leitura da temperatura')
                    else:
                        self.update_gui.emit('      Reprovado no teste de leitura da temperatura')

                    for s in range(0, len(mod_result4[serial.index(item)])):
                        if round(mod_result4[serial.index(item)][s]) == 15:
                            if test[3]:
                                test[3] = True
                            else:
                                test[3] = False
                    if test[3]:
                        self.update_gui.emit('      Aprovado no teste de leitura da tensão de entrada')
                    else:
                        self.update_gui.emit('      Reprovado no teste de leitura da tensão de entrada')

                    if test == [True for t in range(4)]:
                        log.test_result = 'Aprovado'
                    else:
                        log.test_result = 'Reprovado'

                    log.iload0 = mod_result1[serial.index(item)][0]
                    log.iload1 = mod_result1[serial.index(item)][1]
                    log.iload2 = mod_result1[serial.index(item)][2]
                    log.iload3 = mod_result1[serial.index(item)][3]
                    log.iload4 = mod_result1[serial.index(item)][4]
                    log.iload5 = mod_result1[serial.index(item)][5]

                    log.vload0 = mod_result1[serial.index(item)][0]
                    log.vload1 = mod_result1[serial.index(item)][1]
                    log.vload2 = mod_result1[serial.index(item)][2]
                    log.vload3 = mod_result1[serial.index(item)][3]
                    log.vload4 = mod_result1[serial.index(item)][4]
                    log.vload5 = mod_result1[serial.index(item)][5]

                    log.vdclink0 = mod_result2[serial.index(item)][0]
                    log.vdclink1 = mod_result2[serial.index(item)][1]
                    log.vdclink2 = mod_result2[serial.index(item)][2]
                    log.vdclink3 = mod_result2[serial.index(item)][3]
                    log.vdclink4 = mod_result2[serial.index(item)][4]
                    log.vdclink5 = mod_result2[serial.index(item)][5]

                    log.temperatura0 = mod_result3[serial.index(item)][0]
                    log.temperatura1 = mod_result3[serial.index(item)][1]
                    log.temperatura2 = mod_result3[serial.index(item)][2]
                    log.temperatura3 = mod_result3[serial.index(item)][3]
                    log.temperatura4 = mod_result3[serial.index(item)][4]
                    log.temperatura5 = mod_result3[serial.index(item)][5]

                    log.details = ""

                    self.update_gui.emit('Módulo ' + str(serial.index(item)+1)\
                                        + ' ' + log.test_result)
                    #log_res = self._send_to_server(log)
                    #response[serial.index(item)] = log_res

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

from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

import sys
sys.path.insert(0, '../test_config/')

from test_config import ResolutionConfig


class Resolution(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.cfg = ResolutionConfig()


    def resolution_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                    ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                  ' + str(self.cfg.inst_addr))
        print('Lista de Bastidores:                     ' + str(self.cfg.bastidor_list))
        print('Lista de módulos para teste individual:  ' + str(self.cfg.individual_module_list))
        print('Lista de valores de corrente de saída:   ' + str(self.cfg.idc_list))
        print('Lista de canais do multimetro:           ' + str(self.cfg.channel_list))
        print('Tempo de WarmUp dos módulos de potência: ' + str(self.cfg.warmup_time))
        print('Número de bits para o teste:             ' + str(self.cfg.nbits))

        # ctrl = input('\nOs dados estão corretos?(y/n): ')
        ctrl = 'y'
        ################################################################################
        ################################################################################


        ################################################################################
        ############################# INICIO DO TESTE ##################################
        ################################################################################
        if ctrl == 'y':
            self.drs.Connect(self.cfg.com_port)

            for i in range(len(self.cfg.bastidor_list)):
                for module in self.cfg.individual_module_list[i]:

                    ################################################################################
                    ######################## CONFIGURANDO O MULTIMETRO #############################
                    ################################################################################
                    print(i)
                    print(module)
                    channel = str(self.cfg.channel_list[i][self.cfg.individual_module_list[i].index(module)])

                    rm   = visa.ResourceManager()
                    inst = rm.open_resource(self.cfg.inst_addr)

                    del inst.timeout

                    inst.write('CONF:VOLT:DC (@'           + channel + ')')
                    time.sleep(0.5)
                    inst.write('SENS:VOLT:DC:NPLC 200, (@' + channel + ')')
                    time.sleep(0.5)
                    ################################################################################
                    ################################################################################


                    for idc in self.cfg.idc_list:
                        _file = open('Resolucao_' + str(module) + '_NS' + str(self.cfg.bastidor_list[i]) + '.csv', 'a')
                        _file.write('IDC = ' + str(idc) + 'A\n')
                        _file.write('time stamp;VDC;Ref;temp\n')

                        self.drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        self.drs.reset_interlocks()
                        time.sleep(0.5)
                        self.drs.turn_on()
                        time.sleep(0.5)
                        self.drs.closed_loop()
                        time.sleep(0.5)
                        reference = idc - ((10/(2 ** self.cfg.nbits)) *15)
                        self.drs.set_slowref(reference)

                        print('\nAguardando tempo de WarmUp...')
                        time.sleep(self.cfg.warmup_time)
                        print('#########################################################################')
                        print('\nInicio do teste do modulo ' + str(module) + ', IDC = ' + str(idc) + 'A:')
                        print(str(datetime.now()))

                        for j in range(30):
                            if not j == 0:
                                reference = reference + (10/(2 ** self.cfg.nbits))

                            print('\nReference: ' + str(reference))
                            self.drs.set_slowref(reference)
                            time.sleep(0.5)
                            temperature = str(self.drs.read_bsmp_variable(30, 'float'))
                            write_reference = str(reference)
                            time.sleep(5)

                            for k in range(5):
                                inst.write('READ?')
                                read = str(float(inst.read()))
                                _file.write(str(datetime.now()) + ';'       +\
                                            read.replace('.', ',') + ';'    +\
                                            write_reference.replace('.', ',') + ';' +\
                                            temperature.replace('.', ',') + '\n')

                        print('\nFim do teste: ')
                        print(str(datetime.now()))
                        print('#########################################################################')

                        self.drs.turn_off()
                        _file.close()
                    inst.close()
        ################################################################################
        ############################### FIM DO TESTE ###################################
        ################################################################################


        else:
            print('Corrija os dados e reinicie o teste!')

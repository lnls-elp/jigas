from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

import sys
sys.path.insert(0, '../test_config/')

from test_config import LinearityConfig


class Linearity(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.cfg = LinearityConfig()


    def linearity_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                    ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                  ' + str(self.cfg.inst_addr))
        print('Lista de Bastidores:                     ' + str(self.cfg.bastidor_list))
        print('Lista de módulos para teste individual:  ' + str(self.cfg.individual_module_list))
        print('Lista de canais do multimetro:           ' + str(self.cfg.channel_list))
        print('Tempo de WarmUp dos módulos de potência: ' + str(self.cfg.warmup_time))
        print('Tempo de estabilização da medida:        ' + str(self.cfg.stb_time))

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
                    channel = str(self.cfg.channel_list[i][self.cfg.individual_module_list[i].index(module)])
                    print(channel)
                    rm   = visa.ResourceManager()
                    inst = rm.open_resource(self.cfg.inst_addr)

                    del inst.timeout

                    inst.write('CONF:VOLT:DC (@'           + channel + ')')
                    time.sleep(0.5)
                    inst.write('SENS:VOLT:DC:NPLC 200, (@' + channel + ')')
                    time.sleep(0.5)
                    ################################################################################
                    ################################################################################


                    _file = open('Linearidade_' + str(module) + '_NS' + str(self.cfg.bastidor_list[i]) + '.csv', 'a')
                    _file.write('time stamp;VDC;Ref;temp\n')

                    reference = -10
                    self.drs.SetSlaveAdd(module)
                    time.sleep(0.5)
                    self.drs.reset_interlocks()
                    time.sleep(0.5)
                    self.drs.turn_on()
                    time.sleep(0.5)
                    self.drs.closed_loop()
                    time.sleep(0.5)
                    self.drs.set_slowref(-10)

                    print('Aguardando tempo de WarmUp...')
                    time.sleep(self.cfg.warmup_time)
                    print('Inicio do teste do modulo ' + str(module) + ':')
                    print(str(datetime.now()))

                    for j in range(201):
                        reference = -10 + (j * 0.1)
                        print(reference)
                        self.drs.set_slowref(reference)
                        time.sleep(self.cfg.stb_time) # alterar para 120

                        write_reference = str(reference)
                        temperature = str(self.drs.read_bsmp_variable(30, 'float'))

                        inst.write('READ?')
                        read = str(float(inst.read()))
                        _file.write(str(datetime.now()) + ';' + read.replace('.', ',') +\
                                    ';' + write_reference.replace('.', ',')            +\
                                    ';' + temperature.replace('.', ',') + '\n')

                    self.drs.turn_off()
                    _file.close()

                    print('Fim do teste: ')
                    print(str(datetime.now()))
        ################################################################################
        ############################### FIM DO TESTE ###################################
        ################################################################################

        else:
            print('Corrija os dados e reinicie o teste!')
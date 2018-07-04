from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

import sys
sys.path.insert(0, '../test_config/')

from test_config import CrossTalkConfig


class CrossTalk(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.cfg = CrossTalkConfig()


    def cross_talk_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                    ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                  ' + str(self.cfg.inst_addr))
        print('Bastidores:                              ' + str(self.cfg.bastidor_list))
        print('Lista de módulos para teste:             ' + str(self.cfg.individual_module_list))
        print('Lista de valores de corrente de teste:   ' + str(self.cfg.idc_set_test_list))
        print('Lista de valores de corrente auxiliares: ' + str(self.cfg.idc_set_current_list))
        print('Lista de canais do multímetro:           ' + str(self.cfg.channel_list))
        print('Tempo de degrau de corrente:             ' + str(self.cfg.step_time))
        print('Tempo de aquecimento dos módulos:        ' + str(self.cfg.warmup_time))
        # ctrl = input('\nOs dados estão corretos?(y/n): ')
        ctrl = 'y'
        ################################################################################
        ################################################################################


        ################################################################################
        ############################# INICIO DO TESTE ##################################
        ################################################################################
        if ctrl == 'y':
            self.drs.Connect(self.cfg.com_port)
            for k in range(len(self.cfg.bastidor_list)):
                channels = ''
                for l in self.cfg.channel_list[k]:
                    channels = channels + str(l) + ','

                for module in self.cfg.individual_module_list[k]:
                    auxiliary_module_list = []
                    for i in self.cfg.individual_module_list[k]:
                        auxiliary_module_list.append(i)
                    auxiliary_module_list.remove(module)

                    print(auxiliary_module_list)
                    for module_ in self.cfg.individual_module_list[k]:
                        self.drs.SetSlaveAdd(module_)
                        time.sleep(0.5)
                        self.drs.reset_interlocks()
                        time.sleep(0.5)
                        self.drs.turn_on()
                        time.sleep(0.5)
                        self.drs.closed_loop()
                    ################################################################################
                    ######################## CONFIGURANDO O MULTIMETRO #############################
                    ################################################################################
                    rm   = visa.ResourceManager()
                    inst = rm.open_resource(self.cfg.inst_addr)

                    del inst.timeout

                    inst.write('CONF:VOLT:DC (@'          + channels + ')')
                    time.sleep(0.5)
                    inst.write('SENS:VOLT:DC:NPLC 1, (@' + channels + ')')
                    time.sleep(0.5)
                    inst.write('ROUT:SCAN (@'             + channels + ')')
                    time.sleep(0.5)
                    ################################################################################
                    ################################################################################

                    for idc in self.cfg.idc_set_test_list:
                        self.drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        self.drs.reset_interlocks()
                        time.sleep(0.5)
                        self.drs.set_slowref(idc)

                        print('Aguardando tempo de WarmUp...')
                        time.sleep(self.cfg.warmup_time)

                        _file = open('CrossTalk_' + str(module) + '_idc_' + str(idc) + '_NS' + str(self.cfg.bastidor_list[k]) + '.csv', 'a')
                        _file.write('time stamp')

                        channels_write = channels.split(',')

                        for m in channels_write:
                            _file.write(';' + 'CH ' + str(m))
                        _file.write('\n')

                        for step in self.cfg.idc_set_current_list:
                            for aux in auxiliary_module_list:
                                self.drs.SetSlaveAdd(aux)
                                time.sleep(0.5)
                                self.drs.reset_interlocks()
                                time.sleep(0.5)
                                self.drs.set_slowref(step)
                                time.sleep(0.5)

                            for n in range(self.cfg.step_time):
                                _file.write(str(datetime.now()))

                                inst.write('READ?')
                                read = inst.read()
                                read = read.split(',')

                                for value in read:
                                    _file.write(';' + value.replace('.', ','))

                                time.sleep(0.77)

                    for module__ in self.cfg.individual_module_list[k]:
                        self.drs.SetSlaveAdd(module__)
                        time.sleep(0.5)
                        self.drs.reset_interlocks()
                        time.sleep(0.5)
                        self.drs.turn_off()
                    inst.close()

        else:
            print('Corrija os dados e reinicie o teste!')

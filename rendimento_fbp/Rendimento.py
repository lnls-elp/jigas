from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

import sys
sys.path.insert(0, '../test_config/')

from test_config import EficiencyConfig


class Eficiency(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.now = datetime.now()
        self.cfg = EficiencyConfig()


    def eficiency_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                    ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                  ' + str(self.cfg.inst_addr))
        print('Bastidor:                                ' + str(self.cfg.bastidor))
        print('Lista de módulos para teste:             ' + str(self.cfg.individual_module_list))
        print('Endereço do Slot:                        ' + str(self.cfg.slot_address))
        print('Lista de valores de corrente de saída:   ' + str(self.cfg.ps_iout))
        print('Canal de leitura da corrente de entrada: ' + str(self.cfg.input_current_channel))
        print('Canal de leitura da corrente de saída:   ' + str(self.cfg.output_current_channel))
        print('Canal de leitura da tensão de entrada:   ' + str(self.cfg.input_voltage_channel))
        print('Canal de leitura da tensão de saída:     ' + str(self.cfg.output_voltage_channel))
        print('Tempo de aquecimento dos módulos:        ' + str(self.cfg.warmup_time))
        ctrl = input('\nOs dados estão corretos?(y/n): ')
        ################################################################################
        ################################################################################


        ################################################################################
        ############################# INICIO DO TESTE ##################################
        ################################################################################
        if ctrl == 'y':
            self.drs.Connect(self.cfg.com_port)
            time.sleep(0.5)
            self.drs.SetSlaveAdd(self.cfg.slot_address)
            time.sleep(0.5)

            ################################################################################
            ######################## CONFIGURANDO O MULTIMETRO #############################
            ################################################################################
            rm   = visa.ResourceManager()
            inst = rm.open_resource(self.cfg.inst_addr)

            del inst.timeout

            inst.write('CONF:VOLT:DC (@' + str(self.cfg.input_current_channel) + ','+
                    str(self.cfg.output_current_channel)+ ',' + str(self.cfg.input_voltage_channel) +
                    ',' + str(self.cfg.output_voltage_channel) + ')')
            time.sleep(0.5)
            inst.write('SENS:VOLT:DC:NPLC 10, (@' + str(self.cfg.input_current_channel) + ',' +
                    str(self.cfg.output_current_channel) + ',' + str(self.cfg.input_voltage_channel) +
                    ',' + str(self.cfg.output_voltage_channel) + ')')
            time.sleep(0.5)
            inst.write('ROUT:SCAN (@' + str(self.cfg.input_current_channel) + ',' +
                    str(self.cfg.output_current_channel) + ',' +
                    str(self.cfg.input_voltage_channel) + ',' +
                    str(self.cfg.output_voltage_channel) + ')')
            time.sleep(0.5)

            pause = input('\nConecte o primeiro módulo a ser testado no slot 1 e tecle enter')
            for module in self.cfg.individual_module_list:
                print('\nLigando o módulo...\n')
                self.drs.turn_on()
                time.sleep(0.5)
                self.drs.closed_loop()
                time.sleep(0.5)

                _file = open('rendimento_modulo' + str(module) + '.csv', 'a')
                _file.write('self.cfg.bastidor ' + str(self.cfg.bastidor) + '\n')
                _file.write('Ii [A];Io [A];Vi [V];Vo [V];Pi [W];Po [W]; rendimento [%]\n')

                for i in self.cfg.ps_iout:
                    print('Realizando medidas com ' + str(i) + 'A')
                    self.drs.set_slowref(i)
                    print('\nAguardando aquecimento do módulo...\n')
                    time.sleep(self.cfg.warmup_time)
                    inst.write('READ?')
                    read = inst.read()
                    read = read.split(',')

                    for j in read:
                        read[read.index(j)] = float(j)

                    read.append(read[0] * read[2])
                    read.append(read[1] * read[3])
                    read.append((read[5] / read[4]) * 100)

                    for k in read:
                        value = str(k)
                        _file.write(value.replace('.', ',') + ';')
                    _file.write('\n')

                self.drs.turn_off()
                _file.close()

                if len(self.cfg.individual_module_list) > self.cfg.individual_module_list.index(module)+1:
                    pause = input('Insira o módulo ' + str(self.cfg.individual_module_list[self.cfg.individual_module_list.index(module)+1]))
                else:
                    pass
            print('Fim do teste')
            inst.close()
        ################################################################################
        ############################### FIM DO TESTE ###################################
        ################################################################################
        
        
        else:
            print('Corrija os dados e reinicie o teste!')

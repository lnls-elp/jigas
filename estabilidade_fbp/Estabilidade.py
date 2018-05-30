from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

import sys
sys.path.insert(0, '../test_config/')

from test_config import StabilityConfig


class Stability(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.cfg = StabilityConfig()


    def stability_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                         ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                       ' + str(self.cfg.inst_addr))
        print('Lista de Bastidores:                          ' + str(self.cfg.bastidor_list))
        print('Lista de módulos para teste individual:       ' + str(self.cfg.individual_module_list))
        print('Lista de canais do multimetro:                ' + str(self.cfg.channel_list))
        print('Canal de medição da temperatura ambiente:     ' + str(self.cfg.ambient_temperature_channel))
        print('Período de amostragem:                        ' + str(self.cfg.sampling_period))
        print('Tempo de esfriamento dos módulos de potência: ' + str(self.cfg.cooling_time))
        print('Lista de correntes de teste:                  ' + str(self.cfg.idc_list))
        print('Tempo de teste:                               ' + str(self.cfg.test_time))
        # ctrl = input('\nOs dados estão corretos?(y/n): ')
        ctrl = 'y'
        ################################################################################
        ################################################################################


        ################################################################################
        ############################# INICIO DO TESTE ##################################
        ################################################################################
        if ctrl == 'y':
            self.drs.Connect(self.cfg.com_port)

            vdc_channels = ''
            count = 0
            all_channels_list = []
            for i in range(len(self.cfg.bastidor_list)):
                for module in self.cfg.individual_module_list[i]:
                    vdc_channels = vdc_channels + str(self.cfg.channel_list[i][self.cfg.individual_module_list[i].index(module)]) + ','
                    all_channels_list.append(self.cfg.channel_list[i][self.cfg.individual_module_list[i].index(module)])
                    count = count + 1
            all_channels_list.append(self.cfg.ambient_temperature_channel)
            all_channels_list = sorted(all_channels_list)
            scan_channels = vdc_channels + str(self.cfg.ambient_temperature_channel)

            ################################################################################
            ######################## CONFIGURANDO O MULTIMETRO #############################
            ################################################################################
            rm   = visa.ResourceManager()
            inst = rm.open_resource(self.cfg.inst_addr)

            del inst.timeout

            inst.write('CONF:VOLT:DC (@'           + vdc_channels + ')')
            time.sleep(0.5)
            inst.write('SENS:VOLT:DC:NPLC 200, (@' + vdc_channels + ')')
            time.sleep(0.5)

            inst.write('CONF:TEMP RTD, 85, (@'                  + str(self.cfg.ambient_temperature_channel) + ')')
            time.sleep(0.5)
            inst.write('SENS:TEMP:TRAN:FRTD:RES 100, (@' + str(self.cfg.ambient_temperature_channel) + ')')
            time.sleep(0.5)

            inst.write('ROUT:SCAN (@' + scan_channels + ')')
            time.sleep(0.5)
            ################################################################################
            ################################################################################

            file_name_list = []

            for bastidor in self.cfg.bastidor_list:
                file_name_list.append('Estabilidade_NS' + str(bastidor) + '.csv')

            for file_name in file_name_list:
                _file = open(file_name, 'a')
                _file.write('time stamp;')

                for i in self.cfg.individual_module_list[file_name_list.index(file_name)]:
                    _file.write('CH' + str(i) + ';')
                _file.write('temp_modulo1;temp_modulo2;temp_modulo3;temp_modulo4;')
                _file.write('CH' + str(self.cfg.ambient_temperature_channel) + '\n')
                _file.close()

            for idc in self.cfg.idc_list:
                print('\nInício do teste de estabilidade com módulos a ' + str(idc) + 'A')
                print('Aguardando tempo de esfriamento dos módulos...')
                time.sleep(self.cfg.cooling_time)
                print('Início do teste...')

                for bastidor in self.cfg.bastidor_list:
                    for module in self.cfg.individual_module_list[self.cfg.bastidor_list.index(bastidor)]:
                        self.drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        self.drs.reset_interlocks()
                        time.sleep(0.5)
                        self.drs.turn_on()
                        time.sleep(0.5)
                        self.drs.closed_loop()
                        time.sleep(0.5)

                for j in range(len(self.cfg.bastidor_list)):
                    for k in self.cfg.individual_module_list[j]:
                        self.drs.SetSlaveAdd(k)
                        time.sleep(0.5)
                        self.drs.set_slowref(idc)
                        time.sleep(0.5)

                sleep_time = self.cfg.sampling_period - round((count * 6.67) + 0.033)

                for l in range(int(self.cfg.test_time/self.cfg.sampling_period)):
                    inst.write('READ?')
                    read = inst.read()
                    read = read.replace('\n', '')
                    read = read.split(',')

                    for m in file_name_list:
                        _file = open(m, 'a')
                        _file.write(str(datetime.now()) + ';')
                        _file.close()

                    for ch in all_channels_list:
                        for n in range(len(file_name_list)):
                            if ch in self.cfg.channel_list[n]:
                                _file = open(file_name_list[n], 'a')
                                write_ch = str(read[all_channels_list.index(ch)])
                                write_ch = write_ch.replace('.', ',')
                                _file.write(write_ch + ';')
                                _file.close()

                            elif ch == self.cfg.ambient_temperature_channel:
                                write_temp = str(read[all_channels_list.index(ch)])
                                write_temp = write_temp.replace('.', ',')

                    for bastidor in self.cfg.bastidor_list:
                        for module in self.cfg.individual_module_list[self.cfg.bastidor_list.index(bastidor)]:
                            self.drs.SetSlaveAdd(module)
                            time.sleep(0.1)
                            mod_temperature = str(self.drs.read_bsmp_variable(30, 'float'))
                            mod_temperature = mod_temperature.replace('.', ',')

                            _file = open(file_name_list[self.cfg.bastidor_list.index(bastidor)], 'a')
                            _file.write(mod_temperature + ';')
                            _file.close()

                    for name in file_name_list:
                                _file = open(name, 'a')
                                _file.write(write_temp + '\n')
                                _file.close()

                    time.sleep(sleep_time)

                for bastidor in self.cfg.bastidor_list:
                    for module in self.cfg.individual_module_list[self.cfg.bastidor_list.index(bastidor)]:
                        self.drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        self.drs.turn_off()
        ################################################################################
        ############################### FIM DO TESTE ###################################
        ################################################################################

        else:
            print('Corrija os dados e reinicie o teste!')

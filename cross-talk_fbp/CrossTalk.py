from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

# Arquivo de configuração
import test_config

drs = SerialDRS()
now = datetime.now()

# https://www.topster.pt/texto-para-ascii/doom.html

print(' _____ ______  _   _ ______  _____    _____  _     ______ ' )
print('|  __ \| ___ \| | | || ___ )|  _  |  |  ___|| |    | ___ )' )
print('| |  \/| |_/ /| | | || |_/ /| | | |  | |__  | |    | |_/ /' )
print('| | __ |    / | | | ||  __/ | | | |  |  __| | |    |  __/ ' )
print('| |_\ \| |\ \ | |_| || |    \ \_/ /  | |___ | |____| |    ' )
print(' \____/\_| \_| \___/ \_|     \___/   \____/ \_____/\_|    ' )

print(' _____                                  _____         _  _     _               ')
print('/  __ \                                |_   _|       | || |   (_)              ')
print('| /  \/ _ __   ___   ___   ___  ______   | |    __ _ | || | __ _  _ __    __ _ ')
print('| |    |  __| / _ \ / __| / __||______|  | |   / _` || || |/ /| ||  _ \  / _  |')
print('| \__/\| |   | (_) |\__ \ \__ \          | |  | (_| || ||   < | || | | || (_| |')
print(' \____/|_|    \___/ |___/ |___/          \_/   \__,_||_||_|\_\|_||_| |_| \__, |')
print('                                                                          __/ |')
print('                                                                         |___/ ')
time.sleep(3)


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
drs_port = test_config.COMPort
mult_addr = test_config.InstAddr
bastidor_list = test_config.BastidorList
individual_module_list = test_config.IndividualModuleList
idc_set_test_list = test_config.IDC_SetTestList
idc_set_current_list = test_config.IDC_SetCurrentList
channel_list = test_config.ChannelList
step_time = test_config.StepTime
warm_up = test_config.WarmUpTime
################################################################################
################################################################################


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
print('Confirme os dados:\n')
print('Porta de comunicação:                    ' + str(drs_port))
print('Endereço do multímetro:                  ' + str(mult_addr))
print('Bastidores:                              ' + str(bastidor_list))
print('Lista de módulos para teste:             ' + str(individual_module_list))
print('Lista de valores de corrente de teste:   ' + str(idc_set_test_list))
print('Lista de valores de corrente auxiliares: ' + str(idc_set_current_list))
print('Lista de canais do multímetro:           ' + str(channel_list))
print('Tempo de degrau de corrente:             ' + str(step_time))
print('Tempo de aquecimento dos módulos:        ' + str(warm_up))
ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################


################################################################################
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    drs.Connect(drs_port)
    for k in range(len(bastidor_list)):
        channels = ''
        for l in channel_list[k]:
            channels = channels + str(l) + ','

        for module in individual_module_list[k]:
            auxiliary_module_list = []
            for i in individual_module_list[k]:
                auxiliary_module_list.append(i)
            auxiliary_module_list.remove(module)

            print(auxiliary_module_list)
            for module_ in individual_module_list[k]:
                drs.SetSlaveAdd(module_)
                time.sleep(0.5)
                drs.turn_on()
                time.sleep(0.5)
                drs.closed_loop()
            ################################################################################
            ######################## CONFIGURANDO O MULTIMETRO #############################
            ################################################################################
            rm   = visa.ResourceManager()
            inst = rm.open_resource(test_config.InstAddr)

            del inst.timeout

            inst.write('CONF:VOLT:DC (@'          + channels + ')')
            time.sleep(0.5)
            inst.write('SENS:VOLT:DC:NPLC 10, (@' + channels + ')')
            time.sleep(0.5)
            inst.write('ROUT:SCAN (@'             + channels + ')')
            time.sleep(0.5)
            ################################################################################
            ################################################################################

            for idc in idc_set_test_list:
                drs.SetSlaveAdd(module)
                time.sleep(0.5)
                drs.set_slowref(idc)

                print('Aguardando tempo de WarmUp...')
                time.sleep(warm_up)

                _file = open('CrossTalk_' + str(module) + '_idc_' + str(idc) + '_NS' + str(bastidor_list[k]) + '.csv', 'a')
                _file.write('time stamp')

                channels_write = channels.split(',')

                for m in channels_write:
                    _file.write(';' + 'CH ' + str(m))
                _file.write('\n')

                for step in idc_set_current_list:
                    for aux in auxiliary_module_list:
                        drs.SetSlaveAdd(aux)
                        time.sleep(0.5)
                        drs.set_slowref(step)
                        time.sleep(0.5)
                    time.sleep(1)

                    for n in range(step_time):
                        _file.write(str(datetime.now()))

                        inst.write('READ?')
                        read = inst.read()
                        read = read.split(',')

                        for value in read:
                            _file.write(';' + value.replace('.', ','))

                        time.sleep(1)

            for module__ in individual_module_list[k]:
                drs.SetSlaveAdd(module__)
                time.sleep(0.5)
                drs.turn_off()
            inst.close()

else:
    print('Corrija os dados e reinicie o teste!')

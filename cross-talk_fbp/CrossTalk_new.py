from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

# Arquivo de configuração
import crosstalk_config as conf

drs = SerialDRS()
now = datetime.now()

# https://www.topster.pt/texto-para-ascii/doom.html

print(' _____ ______  _   _ ______  _____    _____  _     ______ ' )
print('|  __ \| ___ \| | | || ___ )|  _  |  |  ___|| |    | ___ )' )
print('| |  \/| |_/ /| | | || |_/ /| | | |  | |__  | |    | |_/ /' )
print('| | __ |    / | | | ||  __/ | | | |  |  __| | |    |  __/ ' )
print('| |_\ \| |\ \ | |_| || |    \ \_/ /  | |___ | |____| |    ' )
print(' \____/\_| \_| \___/ \_|     \___/   \____/ \_____/\_|    ' )
time.sleep(3)

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
print('\nConfirme os dados:\n')
print('Porta de comunicação:            ' + conf.COMPort)
print('Endereço do multímetro:          ' + conf.InstAddr)
print('Tempo de WarmUp:                 ' + str(conf.WarmUpTime))

print('Lista de Bastidores e endereços:')
for i in range(len(conf.BAMC_list)):
    print('                                 ' + str(conf.BAMC_list[i][0:2]))

print('Lista de módulos e canais:')
for j in range(len(conf.BAMC_list)):
    for k in range(len(conf.BAMC_list[j][2])):
        print('                                 ' + str(conf.BAMC_list[j][2][k]))

ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################


################################################################################
############################# FUNÇÕES INTERNAS #################################
################################################################################
def init_module(drs_port, drs_addr, module, idc):
    print('Inicializando módulo' + module + '...')
    drs.Connect(drs_port)
    time.sleep(1)
    drs.SetSlaveAdd(drs_addr)
    time.sleep(1)
    drs.Config_nHRADC(4)
    time.sleep(5)

    if module == 'modulo 1':
        drs.TurnOn(1)
    elif module == 'modulo 2':
        drs.TurnOn(2)
    elif module == 'modulo 3':
        drs.TurnOn(4)
    elif module == 'modulo 4':
        drs.TurnOn(8)

    time.sleep(1)

    if module == 'modulo 1':
        drs.ClosedLoop(1)
    elif module == 'modulo 2':
        drs.ClosedLoop(2)
    elif module == 'modulo 3':
        drs.ClosedLoop(4)
    elif module == 'modulo 4':
        drs.ClosedLoop(8)

    time.sleep(1)

    if   module == 'modulo 1':
        drs.SetISlowRefx4(idc, 0, 0, 0)
    elif module == 'modulo 2':
        drs.SetISlowRefx4(0, idc, 0, 0)
    elif module == 'modulo 3':
        drs.SetISlowRefx4(0, 0, idc, 0)
    elif module == 'modulo 4':
        drs.SetISlowRefx4(0, 0, 0, idc)
    time.sleep(1)

def slow_ref(test_module, idc_module, idc_aux):
    if module == 'modulo 1':
        drs.SetISlowRefx4(idc_module, idc_aux, idc_aux, idc_aux)

    elif module == 'modulo 2':
        drs.SetISlowRefx4(idc_aux, idc_module, idc_aux, idc_aux)

    elif module == 'modulo 3':
        drs.SetISlowRefx4(idc_aux, idc_aux, idc_module, idc_aux)

    elif module == 'modulo 4':
        drs.SetISlowRefx4(idc_aux, idc_aux, idc_aux, idc_module)
################################################################################
################################################################################


################################################################################
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    for k in range(len(conf.BAMC_list)):
        channels = ''
        for l in range(0,conf.BAMC_list[k][2],2):
            init_module(conf.COMPort, conf.BAMC_list[k][1], conf.BAMC_list.[k][2][l], 0)
            channels = channels + ',' + conf.BAMC_list[k][2][l+1]

        for module in conf.BAMC_list[k][2]:
            ################################################################################
            ######################## CONFIGURANDO O MULTIMETRO #############################
            ################################################################################
            rm   = visa.ResourceManager()
            inst = rm.open_resource(conf.InstAddr)

            del inst.timeout

            inst.write('CONF:VOLT:DC (@'          + channels + ')')
            time.sleep(0.5)
            inst.write('SENS:VOLT:DC:NPLC 10, (@' + channels + ')')
            time.sleep(0.5)
            inst.write('ROUT:SCAN (@'             + channels + ')')
            time.sleep(0.5)
            ################################################################################
            ################################################################################

            for idc in conf.IDC_SetTestList:
                slow_ref(module, idc, 0)
                time.sleep(conf.WarmUpTime)

                _file = open('CrossTalk_' + module + '_idc_' + str(idc) + '_NS' + bastidor + '.csv', 'a')
                _file.write('time stamp')

                channels = channels.split(',')

                for channel in channels:
                    _file.write(';' + 'CH ' + channel)
                _file.write('\n')

                for step in conf.SetCurrentList:
                    slow_ref(module, idc, step)

                    for m in range(conf.StepTime):
                        _file.write(str(datetime.now()))

                        inst.write('READ?')
                        read = inst.read()
                        read = read.split(',')

                        for value in read:
                            _file.write(';' + value.replace('.', ',') + '\n')

                        time.sleep(1)



else:
    print('Corrija os dados e reinicie o teste!')

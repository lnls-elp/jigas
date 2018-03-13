from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

drs = SerialDRS()
now = datetime.now()


################################################################################
####################### LENDO ARQUIVO DE CONFIGURAÇÃO ##########################
################################################################################
_cfile = open('freqtest_config.csv', 'r')
config = _cfile.read()
_cfile.close()

config = config.split(';')

for i in config:
    config[config.index(i)] = config[config.index(i)].split('|')

for j in config:
    if config[config.index(j)][0] == 'COMPort':
        drs_port = config[config.index(j)][1]
        drs_port = drs_port.replace('\n', '')
        drs_port = drs_port.split(',')

        if len(drs_port) == 1:
            drs_port = drs_port[0]

    elif config[config.index(j)][0] == 'InstAddr':
        mult_addr = config[config.index(j)][1]
        mult_addr = mult_addr.replace('\n', '')
        mult_addr = mult_addr.split(',')

        if len(mult_addr) == 1:
            mult_addr = mult_addr[0]

    elif config[config.index(j)][0] == 'BastidorList':
        bastidor_list = config[config.index(j)][1]
        bastidor_list = bastidor_list.replace('\n', '')
        bastidor_list = bastidor_list.split(',')

        if type(bastidor_list) is not list:
            bastidor_list = aux
            bastidor_list = []
            bastidor_list.append(aux)

    elif config[config.index(j)][0] == 'IndividualModuleList':
        individual_module_list = config[config.index(j)][1]
        individual_module_list = individual_module_list.replace('\n', '')
        individual_module_list = individual_module_list.split(',')

        if type(individual_module_list) is not list:
            individual_module_list = aux
            individual_module_list = []
            individual_module_list.append(aux)

    elif config[config.index(j)][0] == 'ReferenceValueList':
        idc_list = config[config.index(j)][1]
        idc_list = idc_list.replace('\n', '')
        idc_list = idc_list.split(',')

        if type(idc_list) is not list:
            idc_list = aux
            idc_list = []
            idc_list.append(float(aux))
        else:
            for k in idc_list:
                idc_list[idc_list.index(k)] = int(k)

    elif config[config.index(j)][0] == 'ChannelFrequency':
        channel_freq = config[config.index(j)][1]
        channel_freq = channel_freq.replace('\n', '')
        channel_freq = channel_freq.split(',')

        if type(channel_freq) is not list:
            channel_freq = aux
            channel_freq = []
            channel_freq.append(aux)

    elif config[config.index(j)][0] == 'ChannelRMS':
        channel_rms = config[config.index(j)][1]
        channel_rms = channel_rms.replace('\n', '')
        channel_rms = channel_rms.split(',')

        if type(channel_rns) is not list:
            channel_rms = aux
            channel_rms = []
            channel_rms.append(aux)
################################################################################
################################################################################


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
print('Confirme os dados:\n')
print('Porta de comunicação:                             ' + str(drs_port))
print('Endereço do multímetro:                           ' + str(mult_addr))
print('Lista de Bastidores:                              ' + str(bastidor_list))
print('Lista de módulos para teste individual:           ' + str(individual_module_list))
print('Lista de valores de corrente de saída:            ' + str(idc_list))
print('Canal do multímetro para leitura de frequência:   ' + str(channel_list))
print('Canal do multímetro para leitura do valor eficaz: ' + str(warmup_time))

ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################

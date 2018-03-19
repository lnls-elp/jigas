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

        for bastidor in bastidor_list:
            bastidor_list[bastidor_list.index(bastidor)] = bastidor.split(':')

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

    elif config[config.index(j)][0] == 'CtrlLoop':
        ctrl_loop = config[config.index(j)][1]
        ctrl_loop = ctrl_loop.replace('\n', '')
        ctrl_loop = ctrl_loop.split(',')

        if type(ctrl_loop) is not list:
            ctrl_loop = aux
            ctrl_loop = []
            ctrl_loop.append(aux)

    elif config[config.index(j)][0] == 'ChannelFrequency':
        channel_freq = config[config.index(j)][1]
        channel_freq = channel_freq.replace('\n', '')
        channel_freq = channel_freq.split(',')

        if type(channel_freq) is not list:
            channel_freq = aux
            channel_freq = []
            channel_freq.append(str(aux))

    elif config[config.index(j)][0] == 'ChannelRMS':
        channel_rms = config[config.index(j)][1]
        channel_rms = channel_rms.replace('\n', '')
        channel_rms = channel_rms.split(',')

        if type(channel_rms) is not list:
            channel_rms = aux
            channel_rms = []
            channel_rms.append(str(aux))
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
print('Lista de valores de offset:                       ' + str(idc_list))
print('Teste em malha aberta/fechada:                    ' + str(ctrl_loop))
print('Canal do multímetro para leitura de frequência:   ' + str(channel_freq))
print('Canal do multímetro para leitura do valor eficaz: ' + str(channel_rms))

ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################


################################################################################
############################# FUNÇÕES INTERNAS #################################
################################################################################
def init_module(drs_port, drs_addr, module, ctrl_loop, amplitude):
    print('\nInicializando módulo...')
    drs.Connect(drs_port)
    time.sleep(0.5)
    drs.SetSlaveAdd(drs_addr)
    time.sleep(0.5)
    drs.Config_nHRADC(4)
    time.sleep(5)
    drs.OpMode(3)
    time.sleep(0.5)
    drs.ConfigSigGen(0, 0, 0, 0)
    time.sleep(0.5)
    drs.Write_sigGen_Offset(0)
    time.sleep(0.5)
    drs.Write_sigGen_Amplitude(amplitude)
    time.sleep(0.5)
    drs.Write_sigGen_Freq(10)
    time.sleep(0.5)

    if module == 'modulo 1':
        drs.TurnOn(1)
    elif module == 'modulo 2':
        drs.TurnOn(2)
    elif module == 'modulo 3':
        drs.TurnOn(4)
    elif module == 'modulo 4':
        drs.TurnOn(8)

    time.sleep(1)

    if ctrl_loop == 'closed':
        if module == 'modulo 1':
            drs.ClosedLoop(1)
        elif module == 'modulo 2':
            drs.ClosedLoop(2)
        elif module == 'modulo 3':
            drs.ClosedLoop(4)
        elif module == 'modulo 4':
            drs.ClosedLoop(8)

    time.sleep(1)
    drs.EnableSigGen()
    time.sleep(1)

def freq_increment(offset, frequency):
    drs.Write_sigGen_Offset(offset)
    time.sleep(0.5)
    drs.Write_sigGen_Freq(frequency)
    time.sleep(0.5)
################################################################################
################################################################################


################################################################################
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    for a in bastidor_list:
        bastidor = a[0]
        drs_addr = a[1]

        for module in individual_module_list:
            for loop in ctrl_loop:
                ################################################################################
                ######################## CONFIGURANDO O MULTIMETRO #############################
                ################################################################################
                rm   = visa.ResourceManager()
                inst = rm.open_resource(mult_addr)

                del inst.timeout

                inst.write('CONF:FREQ (@'             + channel_freq[0] + ')')
                time.sleep(0.5)
                inst.write('SENS:FREQ:RANG:LOW 3, (@' + channel_freq[0] + ')')
                time.sleep(0.5)

                inst.write('CONF:VOLT:AC (@'           + channel_rms[0] + ')')
                time.sleep(0.5)
                inst.write('SENS:VOLT:AC:BAND 3, (@'   + channel_rms[0] + ')')
                time.sleep(0.5)

                if loop == 'open':
                    inst.write('CALC:SCALE:GAIN 1, (@'    + channel_rms[0] + ')')
                    time.sleep(0.5)
                    inst.write('CALC:SCALE:STATE ON, (@'  + channel_rms[0] + ')')
                    time.sleep(0.5)
                    inst.write('ROUT:SCAN (@' + channel_rms[0] + ',' + channel_freq[0] + ')')

                    print('\nInício do teste de resposta em frequência em malha aberta...')
                    print('\nPor favor, selecione:')
                    print('                       -O ganho do amplificador diferencial para 1')
                    print('                       -A frequência de corte do amplificador diferencial para 100kHz')
                    pause = input('\nTecle enter para continuar')

                elif loop == 'closed':
                    inst.write('CALC:SCALE:GAIN 0.01, (@' + channel_rms[0] + ')')
                    time.sleep(0.5)
                    inst.write('CALC:SCALE:STATE ON, (@'  + channel_rms[0] + ')')
                    time.sleep(0.5)
                    inst.write('ROUT:SCAN (@' + channel_rms[0] + ',' + channel_freq[0] + ')')

                    print('\nInício do teste de resposta em frequência em malha fechada...')
                    print('\nPor favor, selecione:')
                    print('                       -O ganho do amplificador diferencial para 100')
                    print('                       -A frequência de corte do amplificador diferencial para >1MHz')
                    pause = input('\nTecle enter para continuar')
                ################################################################################
                ################################################################################
                for idc in idc_list:
                    _file = open('RespFrequencia_' + module + '_NS' + bastidor + '.csv', 'a')
                    _file.write('IDC = ' + str(idc) + 'A\n')
                    _file.write('time stamp;Set Frequency [Hz];Read Frequency [Hz];Irms [A]\n')

                    if loop == 'open':
                        init_module(drs_port, drs_addr, loop, module, 10)
                    elif loop == 'closed':
                        init_module(drs_port, drs_addr, loop, module, 0.1)

                    for i in range(1, 5):
                        for j in range(1, 10):
                            if (j*(10**i)) > 10000:
                                pass
                            else:
                                frequency = j*(10**i)

                                print('\nTestando módulo com idc = '  + idc\
                                       + ', frequência = ' + frequency + '...')

                                freq_increment(idc, frequency)
                                time.sleep(5)

                                inst.write('READ?')
                                read = inst.read()
                                read = read.split(',')
                                read[0] = str(float(read[0]))
                                read[1] = str(float(read[1]))

                                print('Frequência lida: ' + read[0])
                                print('Irms lida:       ' + read[1])

                                _file.write(str(datetime.now()) + ';' + \
                                            str(frequency)      + ';' + \
                                            read[0].replace('.', ',') + \
                                            read[1].replace('.', ',') + '\n')

                    print('Fim do teste: ')
                    print(str(datetime.now()))

                    if module == 'modulo 1':
                        drs.TurnOff(1)
                    elif module == 'modulo 2':
                        drs.TurnOff(2)
                    elif module == 'modulo 3':
                        drs.TurnOff(4)
                    elif module == 'modulo 4':
                        drs.TurnOff(8)

                    _file.close()

            inst.close()
################################################################################
############################### FIM DO TESTE ###################################
################################################################################


else:
    print('Corrija os dados e reinicie o teste!')

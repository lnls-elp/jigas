from common.pydrs import SerialDRS
from datetime     import datetime
import time
import visa

import test_config

drs = SerialDRS()
now = datetime.now()


################################################################################
####################### LENDO ARQUIVO DE CONFIGURAÇÃO ##########################
################################################################################
drs_port = test_config.COMPort
mult_addr = test_config.InstAddr
bastidor_list = test_config.BastidorList
individual_module_list = test_config.IndividualModuleList
idc_list = test_config.IDCList
ctrl_loop = test_config.CtrlLoop
channel_freq = test_config.ChannelFrequency
channel_rms = test_config.ChannelRMS
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
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    drs.Connect(drs_port)

    for bastidor in bastidor_list:
        for module in individual_module_list:
            for loop in ctrl_loop:
                ################################################################################
                ######################## CONFIGURANDO O MULTIMETRO #############################
                ################################################################################
                rm   = visa.ResourceManager()
                inst = rm.open_resource(mult_addr)

                del inst.timeout

                inst.write('CONF:FREQ (@'             + str(channel_freq) + ')')
                time.sleep(0.5)
                inst.write('SENS:FREQ:RANG:LOW 3, (@' + str(channel_freq) + ')')
                time.sleep(0.5)

                inst.write('CONF:VOLT:AC (@'           + str(channel_rms) + ')')
                time.sleep(0.5)
                inst.write('SENS:VOLT:AC:BAND 3, (@'   + str(channel_rms) + ')')
                time.sleep(0.5)

                if loop == 'open':
                    inst.write('CALC:SCALE:GAIN 1, (@'    + str(channel_rms) + ')')
                    time.sleep(0.5)
                    inst.write('CALC:SCALE:STATE ON, (@'  + str(channel_rms) + ')')
                    time.sleep(0.5)
                    inst.write('ROUT:SCAN (@' + str(channel_freq) + ',' + str(channel_freq) + ')')

                    print('\nInício do teste de resposta em frequência em malha aberta...')
                    print('\nPor favor, selecione:')
                    print('                       -O ganho do amplificador diferencial para 1')
                    print('                       -A frequência de corte do amplificador diferencial para 100kHz')
                    pause = input('\nTecle enter para continuar')

                elif loop == 'closed':
                    inst.write('CALC:SCALE:GAIN 0.01, (@' + str(channel_rms) + ')')
                    time.sleep(0.5)
                    inst.write('CALC:SCALE:STATE ON, (@'  + str(channel_rms) + ')')
                    time.sleep(0.5)
                    inst.write('ROUT:SCAN (@' + str(channel_freq) + ',' + str(channel_rms) + ')')

                    print('\nInício do teste de resposta em frequência em malha fechada...')
                    print('\nPor favor, selecione:')
                    print('                       -O ganho do amplificador diferencial para 100')
                    print('                       -A frequência de corte do amplificador diferencial para >1MHz')
                    pause = input('\nTecle enter para continuar')
                ################################################################################
                ################################################################################
                
                
                for idc in idc_list:
                    _file = open('RespFrequencia_' + str(module) + '_NS' + str(bastidor) + '.csv', 'a')
                    _file.write('IDC = ' + str(idc) + 'A\n')
                    _file.write('time stamp;Set Frequency [Hz];Read Frequency [Hz];Irms [A]\n')

                    amplitude = 0

                    if loop == 'open':
                        amplitude = 10
                        drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        drs.turn_on()
                        time.sleep(0.5)
                        drs.select_op_mode('Cycle')
                        time.sleep(0.5)
                        drs.cfg_siggen(0, 0, 10, amplitude, 0, 0, 0, 0, 0)
                        time.sleep(0.5)

                    elif loop == 'closed':
                        amplitude = 0.1
                        drs.SetSlaveAdd(module)
                        time.sleep(0.5)
                        drs.turn_on()
                        time.sleep(0.5)
                        drs.select_op_mode('Cycle')
                        time.sleep(0.5)
                        drs.cfg_siggen(0, 0, 10, amplitude, 0, 0, 0, 0, 0)
                        time.sleep(0.5)
                        drs.closed_loop()
                        time.sleep(0.5)

                    for i in range(1, 5):
                        for j in range(1, 10):
                            if (j*(10**i)) > 10000:
                                pass
                            else:
                                frequency = j*(10**i)

                                print('\nTestando módulo com idc = '  + str(idc)\
                                      + 'A' + ', frequência = ' + str(frequency) + 'Hz...')

                                if loop == 'open':
                                    drs.set_siggen(frequency, amplitude, idc)
                                elif loop == 'closed':
                                    drs.set_siggen(frequency, amplitude, idc)
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
                                            ';' + read[1].replace('.', ',') + '\n')

                    print('Fim do teste: ')
                    print(str(datetime.now()))

                    drs.turn_off()
                    _file.close()

            inst.close()
################################################################################
############################### FIM DO TESTE ###################################
################################################################################


else:
    print('Corrija os dados e reinicie o teste!')

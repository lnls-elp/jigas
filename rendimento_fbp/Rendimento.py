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
bastidor = test_config.Bastidor
individual_module_list = test_config.IndividualModuleList
slot_address = test_config.SlotAddress
ps_iout = test_config.ReferenceValueList
input_current_channel = test_config.InputCurrentChannel
output_current_channel = test_config.OutputCurrentChannel
input_voltage_channel = test_config.InputVoltageChannel
output_voltage_channel = test_config.OutputVoltageChannel
warm_up = test_config.WarmUpTime

################################################################################
################################################################################


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
print('Confirme os dados:\n')
print('Porta de comunicação:                    ' + str(drs_port))
print('Endereço do multímetro:                  ' + str(mult_addr))
print('Bastidor:                                ' + str(bastidor))
print('Lista de módulos para teste:             ' + str(individual_module_list))
print('Endereço do Slot:                        ' + str(slot_address))
print('Lista de valores de corrente de saída:   ' + str(ps_iout))
print('Canal de leitura da corrente de entrada: ' + str(input_current_channel))
print('Canal de leitura da corrente de saída:   ' + str(output_current_channel))
print('Canal de leitura da tensão de entrada:   ' + str(input_voltage_channel))
print('Canal de leitura da tensão de saída:     ' + str(output_voltage_channel))
print('Tempo de aquecimento dos módulos:        ' + str(warm_up))
ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################


################################################################################
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    drs.Connect(drs_port)
    time.sleep(0.5)
    drs.SetSlaveAdd(slot_address)
    time.sleep(0.5)

    ################################################################################
    ######################## CONFIGURANDO O MULTIMETRO #############################
    ################################################################################
    rm   = visa.ResourceManager()
    inst = rm.open_resource(mult_addr)

    del inst.timeout

    inst.write('CONF:VOLT:DC (@' + str(input_current_channel) + ','+
               str(output_current_channel)+ ',' + str(input_voltage_channel) +
               ',' + str(output_voltage_channel) + ')')
    time.sleep(0.5)
    inst.write('SENS:VOLT:DC:NPLC 10, (@' + str(input_current_channel) + ',' +
               str(output_current_channel) + ',' + str(input_voltage_channel) +
               ',' + str(output_voltage_channel) + ')')
    time.sleep(0.5)
    inst.write('ROUT:SCAN (@' + str(input_current_channel) + ',' +
               str(output_current_channel) + ',' +
               str(input_voltage_channel) + ',' +
               str(output_voltage_channel) + ')')
    time.sleep(0.5)

    pause = input('\nConecte o primeiro módulo a ser testado no slot 1 e tecle enter')
    for module in individual_module_list:
        print('\nLigando o módulo...\n')
        drs.turn_on()
        time.sleep(0.5)
        drs.closed_loop()
        time.sleep(0.5)

        _file = open('rendimento_modulo' + str(module) + '.csv', 'a')
        _file.write('Bastidor ' + str(bastidor) + '\n')
        _file.write('Ii [A];Io [A];Vi [V];Vo [V];Pi [W];Po [W]; rendimento [%]\n')

        for i in ps_iout:
            print('Realizando medidas com ' + str(i) + 'A')
            drs.set_slowref(i)
            print('\nAguardando aquecimento do módulo...\n')
            time.sleep(warm_up)
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

        drs.turn_off()
        _file.close()

        if len(individual_module_list) > individual_module_list.index(module)+1:
            pause = input('Insira o módulo ' + str(individual_module_list[individual_module_list.index(module)+1]))
        else:
            pass
    print('Fim do teste')
    inst.close()
################################################################################
############################### FIM DO TESTE ###################################
################################################################################
else:
    print('Corrija os dados e reinicie o teste!')

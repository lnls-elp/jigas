from common.pydrs import SerialDRS
from DSOX_3024A import DSOX_3024A_USB
import time
import test_config

drs = SerialDRS()
dso = DSOX_3024A_USB()

################################################################################
####################### LENDO ARQUIVO DE CONFIGURAÇÃO ##########################
################################################################################
drs_port = test_config.COMPort
dso_addr = test_config.InstAddr
dso_file = test_config.InstFileConfig
bastidor = test_config.Bastidor
individual_module_list = test_config.IndividualModuleList
group_module_list = test_config.GroupModuleList
ps_iout = test_config.ReferenceValueList
################################################################################
################################################################################


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
print('Confirme os dados:\n')
print('Porta de comunicação:                                  ' + str(drs_port))
print('Endereço do osciloscópio:                              ' + str(dso_addr))
print('Arquivo de configuração do osciloscópio:               ' + str(dso_file))
print('Bastidor testado:                                      ' + str(bastidor))
print('Lista de endereços dos módulos para teste individual:  ' + str(individual_module_list))
print('Lista de endereços dos módulos para teste conjunto:    ' + str(group_module_list))
print('Lista de valores de corrente de saída:                 ' + str(ps_iout))

ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################

################################################################################
############################### ROTINA DE TESTE ################################
################################################################################
if (ctrl == 'y'):
    drs.Connect(drs_port)
    for module in individual_module_list:
        if individual_module_list.index(module) == 0:
            pause = input('\nConecte os cabos de medição para iniciar o teste\n')
        if not module == None:
            module_name = 'modulo ' + str(individual_module_list.index(module) + 1)
            try:
                if not individual_module_list[individual_module_list.index(module) + 1] == None:
                    next_module = 'modulo ' + str(individual_module_list.index(module) + 2)
            except:
                next_module = None

            print('Iniciando medidas isoladas do ' + module_name + '...\n')

            drs.SetSlaveAdd(module)
            time.sleep(0.5)
            drs.turn_on()
            time.sleep(0.5)
            drs.closed_loop()
            time.sleep(0.5)

            dso.connect(dso_addr)
            time.sleep(1)
            dso.setup_config(dso_file)
            time.sleep(5)

            _file = open('ripple_results_iso.csv', 'a')

            _file.write('NS bastidor: ' + str(bastidor) + '\n')
            _file.write(module_name + '\n')
            _file.write("\nCH1: corrente @ 10 Hz - 3 kHz;'1:100\n")
            _file.write("CH2: corrente @ 10 Hz - 500 kHz;'1:1\n")
            _file.write("CH3: tensão @ 10 Hz - 1 MHz;'1:1\n")
            _file.write('\ncorrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
            _file.close()

            for set_iout in ps_iout:
                print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')
                drs.set_slowref(set_iout)

                print('Aguardando ' + str(test_config.WarmUpTime) + ' segundos para maior estabilidade da medida...\n')
                time.sleep(test_config.WarmUpTime) # WarmUpTime

                while round(drs.read_bsmp_variable(27, 'float')) != set_iout:
                    print('Corrente de saída errada')
                    time.sleep(5)

                print('Iniciando processo de escala automática do osciloscópio...\n')
                dso.auto_scale(3)
                print('Realizando medidas...\n')
                vpp_list = dso.single_shot(test_config.Measurements, 3)
                print('Obtendo resultados e salvando imagem da tela...\n')

                pic_name = module_name + '_' + str(set_iout) + 'A_iso'

                rms_list = dso.get_results(3, pic_name)

                _file = open('ripple_results_iso.csv', 'a')
                _file.write(str(set_iout) + ';')

                print('salvando medidas no arquivo...\n')
                for j in vpp_list:
                    write_value = str(j)
                    _file.write(write_value.replace('.', ','))
                    _file.write(';')
                for k in rms_list:
                    write_value = str(k)
                    _file.write(write_value.replace('.', ','))
                    _file.write(';')
                _file.write('\n')
                _file.close()
            drs.turn_off()

            print('**********************************************************')
            if next_module != None:
                pause = input('\nTroque os cabos de medição para medir o ' + next_module + ' e tecle enter\n')
            else:
                print('Fim do teste!!!')

    drs.Connect(drs_port)
    for module in group_module_list:
        if group_module_list.index(module) == 0:
            pause = input('\nConecte os cabos de medição para iniciar o teste\n')
        if not module == None:
            module_name = 'modulo ' + str(group_module_list.index(module) + 1)
            try:
                if not group_module_list[group_module_list.index(module) + 1] == None:
                    next_module = 'modulo ' + str(group_module_list.index(module) + 2)
                else:
                    next_module = None
            except:
                next_module = None

            print('Iniciando medidas conjuntas do ' + module_name + '...\n')
            for i in range(1,5):
                drs.SetSlaveAdd(i)
                time.sleep(0.5)
                drs.turn_on()
                time.sleep(0.5)
                drs.closed_loop()
                time.sleep(0.5)
            drs.set_slowref_fbp(8)
            time.sleep(0.5)
            drs.set_slowref_fbp(10)
            time.sleep(0.5)

            dso.connect(dso_addr)
            time.sleep(1)
            dso.setup_config(dso_file)
            time.sleep(5)

            _file = open('ripple_results_con.csv', 'a')
            _file.write('NS bastidor: ' + str(bastidor) + '\n')
            _file.write(module_name + '\n')
            _file.write("\nCH1: corrente @ 10 Hz - 3 kHz;'1:100\n")
            _file.write("CH2: corrente @ 10 Hz - 500 kHz;'1:1\n")
            _file.write("CH3: tensão @ 10 Hz - 1 MHz;'1:1\n")
            _file.write('\ncorrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
            _file.close()

            for set_iout in ps_iout:
                drs.SetSlaveAdd(module)
                time.sleep(0.5)
                print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')
                drs.set_slowref(set_iout)
                print('Aguardando ' + str(test_config.WarmUpTime) + ' segundos para maior estabilidade da medida...\n')
                time.sleep(test_config.WarmUpTime) # WarmUpTime

                while round(drs.read_bsmp_variable(27, 'float')) != set_iout:
                    print('Corrente de saída errada')
                    time.sleep(5)

                print('Iniciando processo de escala automática do osciloscópio...\n')
                dso.auto_scale(3)
                print('Realizando medidas...\n')
                vpp_list = dso.single_shot(test_config.Measurements, 3)
                print('Obtendo resultados e salvando imagem da tela...\n')

                pic_name = module_name + '_' + str(set_iout) + 'A_con'
                rms_list = dso.get_results(3, pic_name)

                _file = open('ripple_results_con.csv', 'a')
                _file.write(str(set_iout) + ';')

                print('salvando medidas no arquivo...\n')
                for j in vpp_list:
                    write_value = str(j)
                    _file.write(write_value.replace('.', ','))
                    _file.write(';')
                for k in rms_list:
                    write_value = str(k)
                    _file.write(write_value.replace('.', ','))
                    _file.write(';')
                _file.write('\n')
                _file.close()

            for i in range(1, 5):
                drs.SetSlaveAdd(i)
                time.sleep(0.5)
                drs.turn_off()
                time.sleep(0.5)
            print('**********************************************************')
            if next_module != None:
                pause = input('\nTroque os cabos de medição para medir o ' + next_module + ' e tecle enter\n')
            else:
                print('Fim do teste!!!')
else:
    print('\nCorrija os dados e reinicie o teste.\n')
################################################################################
################################################################################

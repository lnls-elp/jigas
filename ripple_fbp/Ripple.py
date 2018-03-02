from common.pydrs import SerialDRS
from DSOX_3024A import DSOX_3024A_USB
import time

drs = SerialDRS()
dso = DSOX_3024A_USB()

_cfile = open('test_config.csv', 'r')
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

    elif config[config.index(j)][0] == 'UdcAddr':
        drs_addr = config[config.index(j)][1]
        drs_addr = drs_addr.replace('\n', '')
        drs_addr = drs_addr.split(',')

        if len(drs_addr) == 1:
            drs_addr = int(drs_addr[0])

    elif config[config.index(j)][0] == 'InstAddr':
        dso_addr = config[config.index(j)][1]
        dso_addr = dso_addr.replace('\n', '')
        dso_addr = dso_addr.split(',')

        if len(dso_addr) == 1:
            dso_addr = dso_addr[0]

    elif config[config.index(j)][0] == 'InstFileConfig':
        dso_file = config[config.index(j)][1]
        dso_file = dso_file.replace('\n', '')
        dso_file = dso_file.split(',')

        if len(dso_file) == 1:
            dso_file = dso_file[0]

    elif config[config.index(j)][0] == 'BastidorList':
        bastidor = config[config.index(j)][1]
        bastidor = bastidor.replace('\n', '')
        bastidor = bastidor.split(',')

        if len(bastidor) == 1:
            bastidor = bastidor[0]

    elif config[config.index(j)][0] == 'IndividualModuleList':
        individual_module_list = config[config.index(j)][1]
        individual_module_list = individual_module_list.replace('\n', '')
        individual_module_list = individual_module_list.split(',')

        if len(individual_module_list) == 1:
            individual_module_list = individual_module_list[0]

    elif config[config.index(j)][0] == 'GroupModuleList':
        group_module_list = config[config.index(j)][1]
        group_module_list = group_module_list.replace('\n', '')
        group_module_list = group_module_list.split(',')

        if len(group_module_list) == 1:
            group_module_list = group_module_list[0]

    elif config[config.index(j)][0] == 'ReferenceValueList':
        ps_iout = config[config.index(j)][1]
        ps_iout = ps_iout.replace('\n', '')
        ps_iout = ps_iout.split(',')

        if len(ps_iout) == 1:
            ps_iout = ps_iout[0]
        else:
            for k in ps_iout:
                ps_iout[ps_iout.index(k)] = int(k)

print('Confirme os dados:\n')
print('Porta de comunicação:                    ' + str(drs_port))
print('Endereço do UDC:                         ' + str(drs_addr))
print('Endereço do osciloscópio:                ' + str(dso_addr))
print('Arquivo de configuração do osciloscópio: ' + str(dso_file))
print('Bastidor testado:                        ' + str(bastidor))
print('Lista de módulos para teste individual:  ' + str(individual_module_list))
print('Lista de módulos para teste conjunto:    ' + str(group_module_list))
print('Lista de valores de corrente de saída:   ' + str(ps_iout))

ctrl = input('\nOs dados estão corretos?(y/n): ')

if (ctrl == 'y'):
    print('\nConfigurando DRS...\n')
    drs.Connect(drs_port)
    time.sleep(1)
    drs.SetSlaveAdd(drs_addr)
    time.sleep(1)
    drs.Config_nHRADC(4)
    time.sleep(5)

    for i in range(2):
    # for i in range(1,2,1):

        # for module in module_list[3:]:
        for module in module_list:
            if i == 0:
                print('Iniciando medidas isoladas do ' + module + '...\n')
                drs.TurnOn(2**module_list.index(module))
                time.sleep(1)
                drs.ClosedLoop(2**module_list.index(module))
            elif i == 1:
                print('Iniciando medidas conjuntas do ' + module + '...\n')
                drs.TurnOn(15)
                time.sleep(1)
                drs.ClosedLoop(15)

            dso.connect(dso_addr)
            time.sleep(1)
            dso.setup_config(dso_file)
            time.sleep(5)

            if i == 0:
                _file = open('ripple_results_iso.csv', 'a')
            elif i == 1:
                _file = open('ripple_results_con.csv', 'a')

            _file.write('NS bastidor: ' + bastidor + '\n')
            _file.write(module + '\n')
            _file.write("\nCH1: corrente @ 10 Hz - 3 kHz;'1:100\n")
            _file.write("CH2: corrente @ 10 Hz - 500 kHz;'1:1\n")
            _file.write("CH3: tensão @ 10 Hz - 1 MHz;'1:1\n")
            _file.write('\ncorrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
            _file.close()

            for set_iout in ps_iout:
                print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')

                if i == 0:
                    if   module == 'modulo 1':
                        drs.SetISlowRefx4(set_iout, 0, 0, 0)
                    elif module == 'modulo 2':
                        drs.SetISlowRefx4(0, set_iout, 0, 0)
                    elif module == 'modulo 3':
                        drs.SetISlowRefx4(0, 0, set_iout, 0)
                    elif module == 'modulo 4':
                        drs.SetISlowRefx4(0, 0, 0, set_iout)

                elif i == 1:
                    if   module == 'modulo 1':
                        drs.SetISlowRefx4(set_iout, 10, 10, 10)
                    elif module == 'modulo 2':
                        drs.SetISlowRefx4(10, set_iout, 10, 10)
                    elif module == 'modulo 3':
                        drs.SetISlowRefx4(10, 10, set_iout, 10)
                    elif module == 'modulo 4':
                        drs.SetISlowRefx4(10, 10, 10, set_iout)

                print('Aguardando 60 segundos para maior estabilidade da medida...\n')
                # time.sleep(60)

                if module_list.index(module) == 0:
                    while round(drs.Read_iMod1()) != set_iout:
                        print('Corrente de saída errada')
                        time.sleep(2)

                elif module_list.index(module) == 1:
                    while round(drs.Read_iMod2()) != set_iout:
                        print('Corrente de saída errada')
                        time.sleep(2)

                elif module_list.index(module) == 2:
                    while round(drs.Read_iMod3()) != set_iout:
                        print('Corrente de saída errada')
                        time.sleep(2)

                elif module_list.index(module) == 3:
                    while round(drs.Read_iMod4()) != set_iout:
                        print('Corrente de saída errada')
                        time.sleep(2)

                print('Iniciando processo de escala automática do osciloscópio...\n')
                dso.auto_scale(3)
                print('Realizando medidas...\n')
                vpp_list = dso.single_shot(10,3)
                print('Obtendo resultados e salvando imagem da tela...\n')

                if i == 0:
                    pic_name = module + '_' + str(set_iout) + 'A_iso'
                elif i == 1:
                    pic_name = module + '_' + str(set_iout) + 'A_con'

                rms_list = dso.get_results(3, pic_name)

                if   i == 0:
                    _file = open('ripple_results_iso.csv', 'a')
                    _file.write(str(set_iout) + ';')
                elif i == 1:
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

            if   i == 0:
                drs.TurnOff(2**module_list.index(module))
            elif i == 1:
                drs.TurnOff(15)

            print('**********************************************************')
            pause = input('\nTroque os cabos de medição para medir o próximo módulo e tecle enter\n')
else:
    print('Corrija os dados e reinicie o teste.')

from common import pydrs.SerialDRS
from DSOX_3024A import DSOX_3024A_USB
import time

drs = SerialDRS()
dso = DSOX_3024A_USB()

dso_addr = 'USB0::2391::6054::MY52492161::INSTR'
dso_file = 'ripple_fbp.scp'

drs_port = 'COM10'
drs_addr = 2

bastidor = '1041182344'

module_list = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']
ps_iout  = [0, 2, 4, 6, 8, 10, -10, -8, -6, -4, -2]

print('\nConfigurando DRS...\n')
drs.Connect(drs_port)
time.sleep(1)
drs.SetSlaveAdd(drs_addr)
time.sleep(1)
drs.Config_nHRADC(4)
time.sleep(1)

for module in module_list:
    print('Iniciando medidas isoladas do ' + module + '...\n')
    drs.TurnOn(2**module_list.index(module))
    time.sleep(0.5)
    drs.ClosedLoop(2**module_list.index(module))

    dso.connect(dso_addr)
    time.sleep(1)
    dso.setup_config(dso_file)
    time.sleep(5)

    _file = open('ripple_results.csv', 'a')
    _file.write('NS bastidor: ' + bastidor + '\n')
    _file.write(module + '\n')
    _file.write('corrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
    _file.close()

    for set_iout in ps_iout:
        print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')
        drs.SetISlowRef(set_iout)
        print('Aguardando 60 segundos para maior estabilidade da medida...\n')
        time.sleep(60)

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
        pic_name = module + '_' + str(set_iout) + 'A'
        rms_list = dso.get_results(3, pic_name)

        _file = open('ripple_results.csv', 'a')
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
    drs.TurnOff(2**module_list.index(module))
    print('**********************************************************')
    pause = input('\nTroque os cabos de medição para medir o próximo módulo e tecle enter\n')

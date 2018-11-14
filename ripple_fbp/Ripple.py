from common.pydrs import SerialDRS
from DSOX_3024A import DSOX_3024A_USB

import SwitchingBoard

import time


import sys
sys.path.insert(0, '../test_config/')

from test_config import RippleConfig


class Ripple(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.dso = DSOX_3024A_USB()
        self.cfg = RippleConfig()


    def ripple_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                                 ' + str(self.cfg.com_port))
        print('Endereço do osciloscópio:                             ' + str(self.cfg.dso_addr))
        print('Arquivo de configuração do osciloscópio:              ' + str(self.cfg.dso_file))
        print('Bastidor testado:                                     ' + str(self.cfg.bastidor))
        print('Lista de endereços dos módulos para teste individual: ' + str(self.cfg.individual_module_list))
        print('Lista de endereços dos módulos para teste conjunto:   ' + str(self.cfg.group_module_list))
        print('Lista de valores de corrente de saída:                ' + str(self.cfg.ps_iout))
        print('Tempo de WarmUp dos módulos de potência:              ' + str(self.cfg.warmup_time))
        print('Switching Mode:                                       ' + str(self.cfg.switching_mode))

        ctrl = input('\nOs dados estão corretos?(y/n): ')
        ################################################################################
        ################################################################################

        ################################################################################
        ############################### ROTINA DE TESTE ################################
        ################################################################################
        if (ctrl == 'y'):
            # self.drs.Connect(self.cfg.com_port, baud=9600) RETIRAR_COMENTARIO
            for module in self.cfg.individual_module_list:
                if self.cfg.individual_module_list.index(module) == 0:
                    if self.cfg.switching_mode:
                        print('Iniciando teste de ripple...')
                        time.sleep(5)
                    else:
                        pause = input('\nConecte os cabos de medição para iniciar o teste\n')
                if not module == None:
                    module_name = 'modulo ' + str(module)
                    try:
                        if not self.cfg.individual_module_list[self.cfg.individual_module_list.index(module) + 1] == None:
                            next_module = 'modulo ' + str(self.cfg.individual_module_list.index(module) + 2)
                    except:
                        next_module = None

                    print('Iniciando medidas isoladas do ' + module_name + '...\n')

                    if self.cfg.switching_mode:
                        print('Comutando saída do ' + module_name + '...\n')
                        SwitchingBoard.switchingBoard_FBP(module)

                    # self.drs.SetSlaveAdd(module) RETIRAR_COMENTARIO
                    # time.sleep(0.5) RETIRAR_COMENTARIO
                    # self.drs.turn_on() RETIRAR_COMENTARIO
                    # time.sleep(0.5) RETIRAR_COMENTARIO
                    # self.drs.closed_loop() RETIRAR_COMENTARIO
                    # time.sleep(0.5) RETIRAR_COMENTARIO

                    self.dso.connect(self.cfg.dso_addr)
                    time.sleep(1)
                    self.dso.setup_config(self.cfg.dso_file)
                    time.sleep(5)

                    _file = open('ripple_results_iso.csv', 'a')

                    _file.write('NS self.cfg.bastidor: ' + str(self.cfg.bastidor) + '\n')
                    _file.write(module_name + '\n')
                    _file.write("\nCH1: corrente @ 10 Hz - 3 kHz;'1:100\n")
                    _file.write("CH2: corrente @ 10 Hz - 500 kHz;'1:1\n")
                    _file.write("CH3: tensão @ 10 Hz - 1 MHz;'1:1\n")
                    _file.write('\ncorrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
                    _file.close()

                    for set_iout in self.cfg.ps_iout:
                        print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')
                        # self.drs.set_slowref(set_iout) RETIRAR_COMENTARIO

                        print('Aguardando ' + str(self.cfg.warmup_time) + ' segundos para maior estabilidade da medida...\n')
                        time.sleep(self.cfg.warmup_time) # WarmUpTime

                        '''while round(self.drs.read_bsmp_variable(27, 'float')) != set_iout:
                            print('Corrente de saída errada')
                            time.sleep(5)
                            RETIRAR_COMENTARIO
                        '''
                        print('Iniciando processo de escala automática do osciloscópio...\n')
                        self.dso.auto_scale(3)
                        print('Realizando medidas...\n')
                        vpp_list = self.dso.single_shot(self.cfg.measurements, 3)
                        print('Obtendo resultados e salvando imagem da tela...\n')

                        pic_name = module_name + '_' + str(set_iout) + 'A_iso'

                        rms_list = self.dso.get_results(3, pic_name)

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
                    # self.drs.turn_off() RETIRAR_COMENTARIO

                    print('**********************************************************')
                    if next_module != None:
                        if self.cfg.switching_mode:
                            SwitchingBoard.switchingBoard_FBP(self.cfg.individual_module_list[self.cfg.individual_module_list.index(module) + 1])
                        else:
                            pause = input('\nTroque os cabos de medição para medir o ' + next_module + ' e tecle enter\n')

                    else:
                        print('Fim do teste!!!')

            # self.drs.Connect(self.cfg.com_port, baud=9600) RETIRAR_COMENTARIO
            for module in self.cfg.group_module_list:
                if self.cfg.group_module_list.index(module) == 0:
                    if self.cfg.switching_mode:
                        print('Iniciando teste de ripple...')
                        time.sleep(5)
                    else:
                        pause = input('\nConecte os cabos de medição para iniciar o teste\n')
                if not module == None:
                    module_name = 'modulo ' + str(module)
                    try:
                        if not self.cfg.group_module_list[self.cfg.group_module_list.index(module) + 1] == None:
                            next_module = 'modulo ' + str(self.cfg.group_module_list.index(module) + 2)
                        else:
                            next_module = None
                    except:
                        next_module = None

                    print('Iniciando medidas conjuntas do ' + module_name + '...\n')

                    if self.cfg.switching_mode:
                        print('Comutando saída do ' + module_name + '...\n')
                        SwitchingBoard.switchingBoard_FBP(module)

                    '''for i in self.cfg.group_module_list:
                        self.drs.SetSlaveAdd(i)
                        time.sleep(0.5)
                        self.drs.turn_on()
                        time.sleep(0.5)
                        self.drs.closed_loop()
                        time.sleep(0.5)
                        self.drs.set_slowref(8)
                        time.sleep(0.5)
                        self.drs.set_slowref(10)
                        time.sleep(0.5)
                        RETIRAR_COMENTARIO
                    '''
                    self.dso.connect(self.cfg.dso_addr)
                    time.sleep(1)
                    self.dso.setup_config(self.cfg.dso_file)
                    time.sleep(5)

                    _file = open('ripple_results_con.csv', 'a')
                    _file.write('NS self.cfg.bastidor: ' + str(self.cfg.bastidor) + '\n')
                    _file.write(module_name + '\n')
                    _file.write("\nCH1: corrente @ 10 Hz - 3 kHz;'1:100\n")
                    _file.write("CH2: corrente @ 10 Hz - 500 kHz;'1:1\n")
                    _file.write("CH3: tensão @ 10 Hz - 1 MHz;'1:1\n")
                    _file.write('\ncorrente;CH1_App;CH2_App;CH3_Vpp;CH1_Arms;CH2_Arms;CH3_Vrms\n')
                    _file.close()

                    for set_iout in self.cfg.ps_iout:
                        # self.drs.SetSlaveAdd(module) RETIRAR_COMENTARIO
                        # time.sleep(0.5) RETIRAR_COMENTARIO
                        print('Iniciando teste com a corrente de ' + str(set_iout) + 'A\n')
                        # self.drs.set_slowref(set_iout) RETIRAR_COMENTARIO
                        print('Aguardando ' + str(self.cfg.warmup_time) + ' segundos para maior estabilidade da medida...\n')
                        time.sleep(self.cfg.warmup_time) # WarmUpTime

                        '''while round(self.drs.read_bsmp_variable(27, 'float')) != set_iout:
                            print('Corrente de saída errada')
                            time.sleep(5)
                            RETIRAR_COMENTARIO
                        '''
                        print('Iniciando processo de escala automática do osciloscópio...\n')
                        self.dso.auto_scale(3)
                        print('Realizando medidas...\n')
                        vpp_list = self.dso.single_shot(self.cfg.measurements, 3)
                        print('Obtendo resultados e salvando imagem da tela...\n')

                        pic_name = module_name + '_' + str(set_iout) + 'A_con'
                        rms_list = self.dso.get_results(3, pic_name)

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

                    '''for i in self.cfg.group_module_list:
                        self.drs.SetSlaveAdd(i)
                        time.sleep(0.5)
                        self.drs.turn_off()
                        time.sleep(0.5)
                        RETIRAR_COMENTARIO
                    '''
                    print('**********************************************************')
                    if next_module != None:
                        if self.cfg.switching_mode:
                            SwitchingBoard.switchingBoard_FBP(self.cfg.individual_module_list[self.cfg.individual_module_list.index(module) + 1])
                        else:
                            pause = input('\nTroque os cabos de medição para medir o ' + next_module + ' e tecle enter\n')

                    else:
                        print('Fim do teste!!!')
        else:
            print('\nCorrija os dados e reinicie o teste.\n')
        ################################################################################
        ################################################################################

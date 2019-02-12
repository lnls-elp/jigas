from common.pydrs import SerialDRS
from DSOX_3024A import DSOX_3024A_USB
from datetime import datetime

import SwitchingBoard

import time
import visa
import math

import sys
sys.path.insert(0, '../test_config/')

from test_config import FrequencyResponseConfig


class FrequencyResponse(object):
    def __init__(self):
        self.drs = SerialDRS()
        self.dso = DSOX_3024A_USB()
        self.cfg = FrequencyResponseConfig()


    def frequency_response_test(self):
        ################################################################################
        ###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
        ################################################################################
        print('Confirme os dados:\n')
        print('Porta de comunicação:                             ' + str(self.cfg.com_port))
        print('Endereço do multímetro:                           ' + str(self.cfg.inst_addr))
        print('Endereço do osciloscópio:                         ' + str(self.cfg.dso_addr))
        print('Arquivo de configuração do osciloscópio:          ' + str(self.cfg.dso_file))
        print('Bastidor:                                         ' + str(self.cfg.bastidor))
        print('Lista de módulos para teste individual:           ' + str(self.cfg.individual_module_list))
        print('Lista de valores de offset:                       ' + str(self.cfg.idc_list))
        print('Teste em malha aberta/fechada:                    ' + str(self.cfg.ctrl_loop))
        print('Canal do multímetro para leitura de frequência:   ' + str(self.cfg.channel_freq))
        print('Canal do multímetro para leitura do valor eficaz: ' + str(self.cfg.channel_rms))
        print('Switching Mode:                                   ' + str(self.cfg.switching_mode))
        print('Referência de amplitude em malha aberta:          ' + str(self.cfg.open_loop_amplitude_reference))
        print('Referência de amplitude em malha fechada:         ' + str(self.cfg.closed_loop_amplitude_reference))
        print('Tolerância para malha aberta:                     ' + str(self.cfg.open_loop_tolerance_adjustment))

        ctrl = input('\nOs dados estão corretos?(y/n): ')
        ################################################################################
        ################################################################################


        ################################################################################
        ############################# INICIO DO TESTE ##################################
        ################################################################################
        if ctrl == 'y':
            self.drs.Connect(self.cfg.com_port)
            self.dso.connect(self.cfg.dso_addr)
            time.sleep(1)
            self.dso.setup_config(self.cfg.dso_file)
            time.sleep(1)

            for i in self.cfg.individual_module_list:
                self.drs.SetSlaveAdd(i)
                time.sleep(0.5)
                self.drs.turn_off()
                time.sleep(0.5)
            self.drs.reset_udc()

            for module in self.cfg.individual_module_list:
                for loop in self.cfg.ctrl_loop:
                    ################################################################################
                    ######################## CONFIGURANDO O MULTIMETRO #############################
                    ################################################################################
                    rm = visa.ResourceManager('@py')
                    inst = rm.open_resource(self.cfg.inst_addr)

                    del inst.timeout

                    inst.write('CONF:FREQ (@'             + str(self.cfg.channel_freq) + ')')
                    time.sleep(0.5)
                    inst.write('SENS:FREQ:RANG:LOW 3, (@' + str(self.cfg.channel_freq) + ')')
                    time.sleep(0.5)

                    inst.write('CONF:VOLT:AC (@'           + str(self.cfg.channel_rms) + ')')
                    time.sleep(0.5)
                    inst.write('SENS:VOLT:AC:BAND 3, (@'   + str(self.cfg.channel_rms) + ')')
                    time.sleep(0.5)

                    if loop == 'open':
                        inst.write('CALC:SCALE:GAIN 0.1, (@'    + str(self.cfg.channel_rms) + ')')
                        time.sleep(0.5)
                        inst.write('CALC:SCALE:STATE ON, (@'  + str(self.cfg.channel_rms) + ')')
                        time.sleep(0.5)
                        inst.write('ROUT:SCAN (@' + str(self.cfg.channel_rms) + ',' + str(self.cfg.channel_freq) + ')')

                        print('\nInício do teste de resposta em frequência em malha aberta do módulo ' + str(module))
                        print('\nPor favor, certifique-se de que o cabo de saída está ligado ao módulo ' + str(module))
                        print('\nPor favor, selecione:')
                        print('                       -O ganho do amplificador diferencial para 10')
                        print('                       -A frequência de corte do amplificador diferencial para 100kHz')
                        
                        if not self.cfg.switching_mode:
                            pause = input('\nTecle enter para continuar')
                        else:
                            for count_time in range(10):
                                print('\n' + str(10 - count_time) + '...')
                                time.sleep(1)

                    elif loop == 'closed':
                        inst.write('CALC:SCALE:GAIN 0.1, (@' + str(self.cfg.channel_rms) + ')')
                        time.sleep(0.5)
                        inst.write('CALC:SCALE:STATE ON, (@'  + str(self.cfg.channel_rms) + ')')
                        time.sleep(0.5)
                        inst.write('ROUT:SCAN (@' + str(self.cfg.channel_freq) + ',' + str(self.cfg.channel_rms) + ')')

                        print('\nInício do teste de resposta em frequência em malha fechada do módulo ' + str(module))
                        print('\nPor favor, certifique-se de que o cabo de saída está ligado ao módulo ' + str(module))
                        print('\nPor favor, selecione:')
                        print('                       -O ganho do amplificador diferencial para 100')
                        print('                       -A frequência de corte do amplificador diferencial para 100kHz')
                        
                        if not self.cfg.switching_mode:
                            pause = input('\nTecle enter para continuar')
                        else:
                            for count_time in range(10):
                                print(str(10 - count_time) + '...')
                                time.sleep(1)
                    ################################################################################
                    ################################################################################


                    for idc in self.cfg.idc_list:
                        _file = open('RespFrequencia_' + str(module) + '_NS' + str(self.cfg.bastidor) + '.csv', 'a')
                        _file.write('IDC = ' + str(idc) + 'A\n')
                        _file.write('time stamp;Set Frequency [Hz];Read Frequency [Hz];Irms [A]\n')

                        if loop == 'open':
                            duty_cycle = [5, 45]
                            iout = []

                            if self.cfg.switching_mode:
                                print('\nComutando saída do módulo ' + str(module) + '...')
                                SwitchingBoard.switchingBoard_FBP(module)

                            self.drs.SetSlaveAdd(module)
                            time.sleep(0.5)
                            self.drs.reset_interlocks()
                            time.sleep(0.5)
                            self.drs.turn_on()
                            time.sleep(0.5)

                            for duty in duty_cycle:
                                self.drs.set_slowref(duty)
                                time.sleep(0.5)
                                iout.append(self.drs.read_bsmp_variable(27, 'float'))
                                time.sleep(0.5)
                            
                            try:
                                alfa = (duty_cycle[1]-duty_cycle[0])/(iout[1]-iout[0])
                            except:
                                print('ERRO! VERIFIQUE AS CONEXÕES DO MÓDULO E REINICIE O CONTROLADOR')

                            amplitude = alfa * (self.cfg.open_loop_amplitude_reference - iout[1]) + duty_cycle[1]
                            
                            if idc != 0:
                                open_loop_offset = alfa * (idc - iout[1]) + duty_cycle[1]
                            else:
                                open_loop_offset = 0

                            print('***********************************************************************')
                            print(amplitude)
                            print('***********************************************************************')
                            print(open_loop_offset)
                            print('***********************************************************************')

                            self.drs.set_slowref(amplitude)
                            time.sleep(0.5)
                            successive_aprox_ctrl = self.drs.read_bsmp_variable(27, 'float')
                            time.sleep(0.5)
                            print('***********************************************************************')
                            print(successive_aprox_ctrl)
                            print('***********************************************************************')

                            while abs(successive_aprox_ctrl - self.cfg.open_loop_amplitude_reference) > abs(self.cfg.open_loop_tolerance_adjustment * self.cfg.open_loop_amplitude_reference):
                                if (successive_aprox_ctrl - self.cfg.open_loop_amplitude_reference) > (self.cfg.open_loop_tolerance_adjustment * self.cfg.open_loop_amplitude_reference):
                                    amplitude = amplitude - 0.01
                                elif (successive_aprox_ctrl - self.cfg.open_loop_amplitude_reference) < (self.cfg.open_loop_tolerance_adjustment * self.cfg.open_loop_amplitude_reference):
                                    amplitude = amplitude + 0.01
                                time.sleep(0.1)
                                print('bla ******************')
                                print(amplitude)
                                self.drs.set_slowref(amplitude)
                                time.sleep(0.1)
                                successive_aprox_ctrl = self.drs.read_bsmp_variable(27, 'float')
                                print(successive_aprox_ctrl)
                                print('bla ******************')

                            if idc != 0:
                                self.drs.set_slowref(open_loop_offset)
                                time.sleep(0.5)
                                successive_aprox_ctrl = self.drs.read_bsmp_variable(27, 'float')
                                time.sleep(0.5)
                                print('***********************************************************************')
                                print(successive_aprox_ctrl)
                                print('***********************************************************************')

                                while abs(successive_aprox_ctrl - idc) > abs(self.cfg.open_loop_tolerance_adjustment * idc):
                                    if (successive_aprox_ctrl - idc) > (self.cfg.open_loop_tolerance_adjustment * idc):
                                        open_loop_offset = open_loop_offset - 0.01
                                    elif (successive_aprox_ctrl - idc) < (self.cfg.open_loop_tolerance_adjustment * idc):
                                        open_loop_offset = open_loop_offset + 0.01
                                    time.sleep(0.1)
                                    print('bla ******************')
                                    print(open_loop_offset)
                                    self.drs.set_slowref(open_loop_offset)
                                    time.sleep(0.1)
                                    successive_aprox_ctrl = self.drs.read_bsmp_variable(27, 'float')
                                    print(successive_aprox_ctrl)
                                    print('bla ******************')
                            else:
                                open_loop_offset = 0

                            print(amplitude)
                            print(open_loop_offset)

                            pause = input('break')

                            self.drs.select_op_mode('Cycle')
                            time.sleep(0.5)
                            self.drs.cfg_siggen(0, 0, 10, amplitude, 0, 0, 0, 0, 0)
                            time.sleep(0.5)
                            self.drs.enable_siggen()
                            time.sleep(0.5)
                            self.dso.do_command(':AUToscale')
                            time.sleep(5)
                            print('VPP:')
                            vp = float(self.dso.single_shot(1, 1))/2
                            print(vp)
                            self.dso.do_command(':RUN')
                            pause = input('break')

                            if 20*math.log10(vp/(self.cfg.open_loop_amplitude_reference/10)) > -1:
                                print('ok')
                            else:
                                print('nok')


                        elif loop == 'closed':
                            amplitude = 0.1
                            self.drs.SetSlaveAdd(module)
                            time.sleep(0.5)
                            self.drs.reset_interlocks()
                            time.sleep(0.5)
                            self.drs.turn_on()
                            time.sleep(0.5)
                            self.drs.select_op_mode('Cycle')
                            time.sleep(0.5)
                            self.drs.cfg_siggen(0, 0, 10, amplitude, 0, 0, 0, 0, 0)
                            time.sleep(0.5)
                            self.drs.closed_loop()
                            time.sleep(0.5)
                            self.drs.enable_siggen()
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

                                        self.drs.set_siggen(frequency, amplitude, open_loop_offset)
                                    elif loop == 'closed':
                                        self.drs.set_siggen(frequency, amplitude, idc)
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

                        self.drs.turn_off()
                        _file.close()

                inst.close()
        ################################################################################
        ############################### FIM DO TESTE ###################################
        ################################################################################


        else:
            print('Corrija os dados e reinicie o teste!')

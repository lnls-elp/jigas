from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

drs = SerialDRS()
now = datetime.now()


################################################################################
####################### LENDO ARQUIVO DE CONFIGURAÇÃO ##########################
################################################################################
_cfile = open('lintest_config.csv', 'r')
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

        if len(bastidor_list) == 1:
            bastidor_list = bastidor_list[0]

    elif config[config.index(j)][0] == 'IndividualModuleList':
        individual_module_list = config[config.index(j)][1]
        individual_module_list = individual_module_list.replace('\n', '')
        individual_module_list = individual_module_list.split(',')

        if len(individual_module_list) == 1:
            individual_module_list = individual_module_list[0]

    elif config[config.index(j)][0] == 'ChannelList':
        channel_list = config[config.index(j)][1]
        channel_list = channel_list.replace('\n', '')
        channel_list = channel_list.split(',')

    elif config[config.index(j)][0] == 'WarmUpTime':
        warmup_time = config[config.index(j)][1]
        warmup_time = warmup_time.replace('\n', '')
        warmup_time = int(warmup_time)

################################################################################
################################################################################


################################################################################
###################### CONFIRMANDO DADOS DE CONFIGURAÇÃO #######################
################################################################################
print('Confirme os dados:\n')
print('Porta de comunicação:                    ' + str(drs_port))
print('Endereço do multímetro:                  ' + str(mult_addr))
print('Lista de Bastidores:                     ' + str(bastidor_list))
print('Lista de módulos para teste individual:  ' + str(individual_module_list))
print('Lista de canais do multimetro:           ' + str(channel_list))
print('Tempo de WarmUp dos módulos de potência: ' + str(warmup_time))

ctrl = input('\nOs dados estão corretos?(y/n): ')
################################################################################
################################################################################


################################################################################
############################# FUNÇÕES INTERNAS #################################
################################################################################
def init_module(drs_port, drs_addr, module, idc):
    print('Inicializando módulo...')
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

def ref_increment(module, idc, count, step):
    if module == 'modulo 1':
        ans = ['', '']
        ref = (idc + (count * step))
        drs.SetISlowRefx4(ref, 0, 0, 0)
        print(drs.Read_iMod1())
        ans[0] = str(ref)
        ans[1] = str(drs.Read_temp1())
        return ans

    elif module == 'modulo 2':
        ans = ['', '']
        ref = (idc + (count * step))
        drs.SetISlowRefx4(0, ref, 0, 0)
        print(drs.Read_iMod2())
        ans[0] = str(ref)
        ans[1] = str(drs.Read_temp2())
        return ans

    elif module == 'modulo 3':
        ans = ['', '']
        ref = (idc + (count * step))
        drs.SetISlowRefx4(0, 0, ref, 0)
        print(drs.Read_iMod3())
        ans[0] = str(ref)
        ans[1] = str(drs.Read_temp3())
        return ans

    elif module == 'modulo 4':
        ans = ['', '']
        ref = (idc + (count * step))
        drs.SetISlowRefx4(0, 0, 0, ref)
        print(drs.Read_iMod4())
        ans[0] = str(ref)
        ans[1] = str(drs.Read_temp4())
        return ans
################################################################################
################################################################################


################################################################################
############################# INICIO DO TESTE ##################################
################################################################################
if ctrl == 'y':
    for bastidor in bastidor_list:
        drs_addr = bastidor_list.index(bastidor) + 1

        for module in individual_module_list:
            ################################################################################
            ######################## CONFIGURANDO O MULTIMETRO #############################
            ################################################################################
            channel = channel_list[individual_module_list.index(module) + \
                      bastidor_list.index(bastidor)                     + \
                      bastidor_list.index(bastidor)*3]

            rm   = visa.ResourceManager()
            inst = rm.open_resource(mult_addr)

            del inst.timeout

            inst.write('CONF:VOLT:DC (@'           + channel + ')')
            time.sleep(0.5)
            inst.write('SENS:VOLT:DC:NPLC 200, (@' + channel + ')')
            time.sleep(0.5)
            ################################################################################
            ################################################################################


            _file = open('Linearidade_' + module + '_NS' + bastidor + '.csv', 'a')
            _file.write('time stamp;VDC;Ref;temp\n')

            init_module(drs_port, drs_addr, module, -10)
            print('Aguardando tempo de WarmUp...')
            time.sleep(warmup_time)
            print('Inicio do teste do ' + module + ':')
            print(str(datetime.now()))

            for i in range(200):
                ref_increment(module, -10, i, 0.1)
                time.sleep(120)

                inst.write('READ?')
                read = str(float(inst.read()))
                _file.write(str(datetime.now()) + ';' + read.replace('.', ',') +\
                            ';' + data[0].replace('.', ',')                    +\
                            ';' + data[1].replace('.', ',') + '\n')
            _file.close()
            
            print('Fim do teste: ')
            print(str(datetime.now()))
################################################################################
############################### FIM DO TESTE ###################################
################################################################################

else:
    print('Corrija os dados e reinicie o teste!')

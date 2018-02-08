from common.pydrs import SerialDRS
from datetime     import datetime

import time
import visa

drs  = SerialDRS()
now  = datetime.now()

rm   = visa.ResourceManager()
inst = rm.open_resource('GPIB::8::INSTR')

bastidor_list = ['1041182343', '1041182349']
drs_port      = 'COM11'
WarmUpTime    = 1#3*3600
nbits         = 18

idc_list     = [5, 0, -5]
module_list  = ['modulo1', 'modulo2', 'modulo3', 'modulo4']
channel_list = ['101', '102', '103', '104', '201', '202', '203', '204']

################################################################################
################################################################################
def config_multimeter(channel):
    del inst.timeout

    inst.write('CONF:VOLT:DC (@'           + channel + ')')
    time.sleep(1)
    inst.write('SENS:VOLT:DC:NPLC 200, (@' + channel + ')')

def read_multimeter():
    inst.write('READ?')
    return str(float(inst.read()))

def init_module(drs_port, drs_addr, module, module_list, idc):
    print('Inicializando módulo...')
    drs.Connect(drs_port)
    time.sleep(1)
    drs.SetSlaveAdd(drs_addr)
    time.sleep(1)
    drs.Config_nHRADC(4)
    time.sleep(5)

    if module == 'modulo1':
        drs.TurnOn(1)
    elif module == 'modulo2':
        drs.TurnOn(2)
    elif module == 'modulo3':
        drs.TurnOn(4)
    elif module == 'modulo4':
        drs.TurnOn(8)

    time.sleep(1)

    if module == 'modulo1':
        drs.ClosedLoop(1)
    elif module == 'modulo2':
        drs.ClosedLoop(2)
    elif module == 'modulo3':
        drs.ClosedLoop(4)
    elif module == 'modulo4':
        drs.ClosedLoop(8)

    time.sleep(1)

    if   module == 'modulo1':
        drs.SetISlowRefx4(idc, 0, 0, 0)
    elif module == 'modulo2':
        drs.SetISlowRefx4(0, idc, 0, 0)
    elif module == 'modulo3':
        drs.SetISlowRefx4(0, 0, idc, 0)
    elif module == 'modulo4':
        drs.SetISlowRefx4(0, 0, 0, idc)
    time.sleep(1)

def ref_increment(module, idc, nbits, count):
    if module == 'modulo1':
        drs.SetISlowRefx4\
        ((idc-(15 * (10/(2 ** nbits)))) + count * (10/(2 ** nbits)), 0, 0, 0)
        print(drs.Read_iMod1())
        return str(drs.Read_temp1())

    elif module == 'modulo2':
        drs.SetISlowRefx4\
        (0, (idc-(15 * (10/(2 ** nbits)))) + count * (10/(2 ** nbits)), 0, 0)
        print(drs.Read_iMod2())
        return str(drs.Read_temp2())

    elif module == 'modulo3':
        drs.SetISlowRefx4\
        (0, 0, (idc-(15 * (10/(2 ** nbits)))) + count * (10/(2 ** nbits)), 0)
        print(drs.Read_iMod3())
        return str(drs.Read_temp3())

    elif module == 'modulo4':
        drs.SetISlowRefx4\
        (0, 0, 0, (idc-(15 * (10/(2 ** nbits)))) + count * (10/(2 ** nbits)))
        print(drs.Read_iMod4())
        return str(drs.Read_temp4())
################################################################################
################################################################################

for bastidor in bastidor_list:
    drs_addr = bastidor_list.index(bastidor) + 1

    for module in module_list:
        config_multimeter(channel_list[module_list.index(module)     + \
                                       bastidor_list.index(bastidor) + \
                                       bastidor_list.index(bastidor)*3])

        for idc in idc_list:
            _file = open('Resolucao_' + module + '_NS' + bastidor + '.csv', 'a')
            _file.write('IDC = ' + str(idc) + 'A\n')
            _file.write('time stamp;VDC;temp\n')

            init_module(drs_port, drs_addr, module, module_list, idc)
            print('Aguardando tempo de WarmUp...')
            time.sleep(WarmUpTime)
            print('Inicio do teste do ' + module + ', IDC = ' + str(idc) + 'A:')
            print(str(datetime.now()))

            for i in range(5):
                temp = ref_increment(module, idc, nbits, i)
                time.sleep(5)
                read = read_multimeter()

                for j in range(1):
                    _file.write(str(datetime.now()) + ';' + read.replace('.', ',') + ';' + str(temp) + '\n')

            print('Fim do teste: ')
            print(str(datetime.now()))

            if module == 'modulo1':
                drs.TurnOff(1)
            elif module == 'modulo2':
                drs.TurnOff(2)
            elif module == 'modulo3':
                drs.TurnOff(4)
            elif module == 'modulo4':
                drs.TurnOff(8)

            _file.close()

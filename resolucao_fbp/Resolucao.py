from common.pydrs import SerialDRS
from datetime import datetime
import time

drs = SerialDRS()
now = datetime.now()

drs_port   = 'COM11'
drs_addr   = 1
bastidor   = '1041182348'
WarmUpTime = 1 #3*3600
StepTime   = 1 #30

nbits  = 18

idc_list    = [5, -5]#[5, 0, -5]
module_list = ['modulo 2', 'modulo 4']#['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']

##############################################################
def init_module(drs_port, drs_addr, module, module_list, idc):
    print('Inicializando módulo...')
    drs.Connect(drs_port)
    time.sleep(1)
    drs.SetSlaveAdd(drs_addr)
    time.sleep(1)
    drs.Config_nHRADC(4)
    time.sleep(5)

    if module == 'modulo 1':
        #drs.TurnOn(2**module_list.index(module))
        drs.TurnOn(1)
    elif module == 'modulo 2':
        drs.TurnOn(2)
    elif module == 'modulo 3':
        drs.TurnOn(4)
    elif module == 'modulo 4':
        drs.TurnOn(8)

    time.sleep(1)

    if module == 'modulo 1':
        #drs.ClosedLoop(2**module_list.index(module))
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

def ref_increment(module, idc, nbits, step_time):
    if module == 'modulo 1':
        for a in range(30):
            drs.SetISlowRefx4((idc-(15 * (10/(2 ** nbits)))) + a * (10/(2 ** nbits)), 0, 0, 0)
            print(drs.Read_iMod1())
            temp = str(drs.Read_temp1())
            _file.write(str(datetime.now()) + ';' + temp.replace('.', ',') + \
            ';' + '--' + ';' + '--' + ';' + '--\n')
            time.sleep(step_time)

    elif module == 'modulo 2':
        for a in range(30):
            drs.SetISlowRefx4(0, (idc-(15 * (10/(2 ** nbits)))) + a * (10/(2 ** nbits)), 0, 0)
            print(drs.Read_iMod2())
            temp = str(drs.Read_temp2())
            _file.write(str(datetime.now()) + ';' + '--' + ';' + temp.replace('.', ',')\
            + ';' + '--' + ';' + '--\n')
            time.sleep(step_time)

    elif module == 'modulo 3':
        for a in range(30):
            drs.SetISlowRefx4(0, 0, (idc-(15 * (10/(2 ** nbits)))) + a * (10/(2 ** nbits)), 0)
            print(drs.Read_iMod3())
            temp = str(drs.Read_temp3())
            _file.write(str(datetime.now()) + ';' + '--' + ';' + '--' + ';' +\
            temp.replace('.', ',') + ';' + '--\n')
            time.sleep(step_time)

    elif module == 'modulo 4':
        for a in range(30):
            drs.SetISlowRefx4(0, 0, 0, (idc-(15 * (10/(2 ** nbits)))) + a * (10/(2 ** nbits)))
            print(drs.Read_iMod4())
            temp = str(drs.Read_temp4())
            _file.write(str(datetime.now()) + ';' + '--' + ';' + '--' + ';' + '--'\
            + ';' + temp.replace('.', ',') + '\n')
            time.sleep(step_time)

_file = open('Resolucao.csv', 'a')
_file.write('time stamp;modulo 1;modulo 2;modulo 3;modulo 4\n')

for idc in idc_list:
    for module in module_list:
        init_module(drs_port, drs_addr, module, module_list, idc)
        print('Aguardando tempo de WarmUp...')
        time.sleep(WarmUpTime)
        print('Inicio do teste do ' + module + ':')
        print(str(datetime.now()))
        ref_increment(module, idc, nbits, StepTime)
        print('Fim do teste: ')
        print(str(datetime.now()))

        if module == 'modulo 1':
            #drs.TurnOff(2**module_list.index(module))
            drs.TurnOff(1)
        elif module == 'modulo 2':
            drs.TurnOff(2)
        elif module == 'modulo 3':
            drs.TurnOff(4)
        elif module == 'modulo 4':
            drs.TurnOff(8)

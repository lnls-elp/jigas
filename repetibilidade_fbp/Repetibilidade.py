from common.pydrs import SerialDRS
from datetime import datetime
import time

drs = SerialDRS()
now = datetime.now()

drs_port   = 'COM11'
drs_addr   = 1
bastidor   = '1041182348'
WarmUpTime = 3*3600
StepTime   = 30

nbits  = 18

idc_list    = [10, 0, -10]
module_list = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']

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
################################################################################
################################################################################
def turn_off(module):
    if module == 'modulo 1':
        drs.TurnOff(1)
    elif module == 'modulo 2':
        drs.TurnOff(2)
    elif module == 'modulo 3':
        drs.TurnOff(4)
    elif module == 'modulo 4':
        drs.TurnOff(8)
################################################################################

_file = open('Repetibilidade.csv', 'a')
_file.write('time stamp;modulo 1;modulo 2;modulo 3;modulo 4\n')

for idc in idc_list:
    for module in module_list:
        init_module(drs_port, drs_addr, module, module_list, idc)
        print('Aguardando tempo de WarmUp...')
        time.sleep(WarmUpTime)
        print('Inicio do teste do ' + module + ':')
        print(str(datetime.now()))

        for i in range(5):
            turn_off(module)
            time.sleep(60)
            init_module(drs_port, drs_addr, module, idc)
            time.sleep(5*60)

        print('Fim do teste: ')
        print(str(datetime.now()))

from common.pydrs import SerialDRS
from datetime import datetime
import time

drs = SerialDRS
now = datetime.now()

drs_port   = '/dev/ttyvirtualcom0'
drs_addr   = 2
bastidor   = '1041182348'
WarmUpTime = 2#2*3600

module_list = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']

print('\nConfigurando DRS...\n')
drs.Connect(drs_port)
time.sleep(1)
drs.SetSlaveAdd(drs_addr)
time.sleep(1)
drs.Config_nHRADC(4)
time.sleep(5)

_file = open('temp_lin_NS' + bastidor + '_.csv', 'a')
_file.write('time stamp'; 'modulo 1'; 'modulo 2'; 'modulo 3'; 'modulo4\n')

for module in module_list:
    drs.TurnOn(2**module_list.index(module))
    time.sleep(1)
    drs.ClosedLoop(2**module_list.index(module))
    time.sleep(1)

    if module_list.index(module) == 0:
        drs.SetISlowRefx4(-10, 0, 0, 0)
        time.sleep()
        _lin_increment(module)

    elif module_list.index(module) == 1:
        drs.SetISlowRefx4(0, -10, 0, 0)
        _lin_increment(module)

    elif module_list.index(module) == 2:
        drs.SetISlowRefx4(0, 0, -10, 0)
        _lin_increment(module)

    elif module_list.index(module) == 3:
        drs.SetISlowRefx4(0, 0, 0, -10)
        _lin_increment(module)

def _lin_increment(module):
    if module == 'modulo 1':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(a/10, 0, 0, 0)
            temp = str(drs.Read_temp1())
            _file.write(str(datetime.now()) + ';' + temp.replace('.', ',') + \
            ';' + '--' + ';' + '--' + ';' + '--' + '\n')

    elif module == 'modulo 2':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, a/10, 0, 0)
            temp = str(drs.Read_temp2())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + temp.replace('.', ',') + ';' + '--' + ';' + '--' + '\n')

    elif module == 'modulo 3':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, 0, a/10, 0)
            temp = str(drs.Read_temp3())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + '--' + ';' + temp.replace('.', ',') + ';' + '--' + '\n')

    elif module == 'modulo 4':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, 0, 0, a/10)
            temp = str(drs.Read_temp1())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + '--' + ';' + '--' + ';' + temp.replace('.', ',') + '\n')

    time.sleep(2)#(2*60)

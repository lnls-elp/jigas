from common.pydrs import SerialDRS
from datetime import datetime
import time

drs = SerialDRS()
now = datetime.now()

drs_port   = 'COM11'
drs_addr   = 2
bastidor   = '1041182349'
WarmUpTime = 2*3600

module_list = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']

###############################################################################
def _lin_increment(module):
    if module == 'modulo 1':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(a/10, 0, 0, 0)
            print(drs.Read_iMod1())
            temp = str(drs.Read_temp1())
            _file.write(str(datetime.now()) + ';' + temp.replace('.', ',') + \
            ';' + '--' + ';' + '--' + ';' + '--' + '\n')
            time.sleep(2*60)

    elif module == 'modulo 2':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, a/10, 0, 0)
            print(drs.Read_iMod2())
            temp = str(drs.Read_temp2())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + temp.replace('.', ',') + ';' + '--' + ';' + '--' + '\n')
            time.sleep(2*60)

    elif module == 'modulo 3':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, 0, a/10, 0)
            print(drs.Read_iMod3())
            temp = str(drs.Read_temp3())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + '--' + ';' + temp.replace('.', ',') + ';' + '--' + '\n')
            time.sleep(2*60)

    elif module == 'modulo 4':
        for a in range(-100, 101, 1):
            drs.SetISlowRefx4(0, 0, 0, a/10)
            print(drs.Read_iMod4())
            temp = str(drs.Read_temp1())
            _file.write(str(datetime.now()) + ';' + '--' + \
            ';' + '--' + ';' + '--' + ';' + temp.replace('.', ',') + '\n')
            time.sleep(2*60)
###############################################################################

print('\nConfigurando DRS...\n')
print(drs.Connect(drs_port))
time.sleep(1)
drs.SetSlaveAdd(drs_addr)
time.sleep(1)
drs.Config_nHRADC(4)
time.sleep(5)

_file = open('temp_lin_NS' + bastidor + '_.csv', 'a')
_file.write('time stamp;modulo 1;modulo 2;modulo 3;modulo 4\n')

for module in module_list:
    drs.TurnOn(2**module_list.index(module))
    time.sleep(1)
    drs.ClosedLoop(2**module_list.index(module))
    time.sleep(1)

    if module_list.index(module) == 0:
        drs.SetISlowRefx4(-10, 0, 0, 0)
        time.sleep(WarmUpTime)
        _lin_increment(module)

    elif module_list.index(module) == 1:
        drs.SetISlowRefx4(0, -10, 0, 0)
        time.sleep(WarmUpTime)
        _lin_increment(module)

    elif module_list.index(module) == 2:
        drs.SetISlowRefx4(0, 0, -10, 0)
        time.sleep(WarmUpTime)
        _lin_increment(module)

    elif module_list.index(module) == 3:
        drs.SetISlowRefx4(0, 0, 0, -10)
        time.sleep(WarmUpTime)
        _lin_increment(module)

    drs.TurnOff(2**module_list.index(module))
    time.sleep(1)

from common import pydrs.SerialDRS
import time

drs = SerialDRS()

drs_port = 'COM10'
drs_addr = 1

bastidor = '1041182344'

module_list = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']

PS_List =        [1, 2, 3, 4]
SetTestList =    [10, 0, -10]
SetCurrentList = [0, 10, 0, -10, 0]

WarmUpTime = 2*3600

print('\nConfigurando DRS e ligando módulos de potência...\n')
drs.Connect(drs_port)
time.sleep(1)
drs.SetSlaveAdd(drs_addr)
time.sleep(1)
drs.Config_nHRADC(4)
time.sleep(1)
drs.TurnOn(0b1111)
time.sleep(0.5)
drs.ClosedLoop(0b1111)
time.sleep(0.5)

#########################################################################
'''                    Inicio do teste de Cross Talk                  '''

for module in module_list:

	for test_current in SetTestList:

		drs.OpMode(3)
		time.sleep(1)
		drs.ConfigSigGen(0, 0, 0, 0)
		time.sleep(1)
		drs.EnableSigGen()
		time.sleep(1)
		drs.Write_sigGen_Freq(module_list.index(module) + 1)
		time.sleep(1)
		drs.Write_sigGen_Amplitude(test_current)
		time.sleep(1)
		drs.Write_sigGen_Freq(module_list.index(module))

		time.sleep(WarmUpTime)

		for aux_current in SetCurrentList:

			drs.Write_sigGen_Amplitude(aux_current)
			time.sleep(0.5)

			print('Fonte 1: ' + str(DRS.Read_iMod1()))
			time.sleep(0.5)
			print('Fonte 2: ' + str(DRS.Read_iMod2()))
			time.sleep(0.5)
			print('Fonte 3: ' + str(DRS.Read_iMod3()))
			time.sleep(0.5)
			print('Fonte 4: ' + str(DRS.Read_iMod4()))
			time.sleep(0.5)
			print('\n')
			time.sleep(58)

drs.TurnOff()
drs.Disconnect()

#########################################################################

from common.pydrs import SerialDRS
from datetime import datetime
import time

drs = SerialDRS()
now = datetime.now()

drs_port = 'COM11'

BastidorList = ['1041182343', '1041182349']
module_list  = ['modulo 1', 'modulo 2', 'modulo 3', 'modulo 4']


PS_List =        [1, 2, 3, 4]
SetTestList =    [10, 0, -10]
SetCurrentList = [0, 10, 0, -10, 0]

WarmUpTime = 2*3600
StepTime   = 60

# o teste dura 50 horas (em média) com um WarmUpTime de 2 horas e um StepTime de 60 min

print(str(now.day) + ',' + str(now.hour) + ':' + str(now.minute))

for bastidor in BastidorList:
	print('\nConfigurando DRS e ligando módulos de potência do bastidor NS.:' + str(bastidor) + '...\n')
	drs.Connect(drs_port)
	time.sleep(1)
	drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
	time.sleep(1)
	drs.Config_nHRADC(4)
	time.sleep(5)
	drs.TurnOn(0b1111)
	time.sleep(1)
	drs.ClosedLoop(0b1111)
	time.sleep(1)

#########################################################################
'''                    Inicio do teste de Cross Talk                  '''

for module in module_list:

	for test_current in SetTestList:

		if module_list.index(module) == 0:
			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				drs.SetISlowRefx4(test_current, 0, 0, 0)
			time.sleep(WarmUpTime)

			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				print('Início de teste:')
				print('			bastidor NS.:' + bastidor)
				print('			' + module)
				for aux_current in SetCurrentList:
					drs.SetISlowRefx4(test_current, aux_current, aux_current, aux_current)
					time.sleep(0.5)
					print('Modulo 1: ' + str(drs.Read_iMod1()))
					time.sleep(0.5)
					print('Modulo 2: ' + str(drs.Read_iMod2()))
					time.sleep(0.5)
					print('Modulo 3: ' + str(drs.Read_iMod3()))
					time.sleep(0.5)
					print('Modulo 4: ' + str(drs.Read_iMod4()))
					time.sleep(0.5)
					print('\n')
					time.sleep(StepTime)

		if module_list.index(module) == 1:
			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				drs.SetISlowRefx4(0, test_current, 0, 0)
			time.sleep(WarmUpTime)

			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				print('Início de teste:')
				print('			bastidor NS.:' + bastidor)
				print('			' + module)
				for aux_current in SetCurrentList:
					drs.SetISlowRefx4(aux_current, test_current, aux_current, aux_current)
					time.sleep(0.5)
					print('Modulo 1: ' + str(drs.Read_iMod1()))
					time.sleep(0.5)
					print('Modulo 2: ' + str(drs.Read_iMod2()))
					time.sleep(0.5)
					print('Modulo 3: ' + str(drs.Read_iMod3()))
					time.sleep(0.5)
					print('Modulo 4: ' + str(drs.Read_iMod4()))
					time.sleep(0.5)
					print('\n')
					time.sleep(StepTime)

		if module_list.index(module) == 2:
			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				drs.SetISlowRefx4(0, 0, test_current, 0)
			time.sleep(WarmUpTime)

			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				print('Início de teste:')
				print('			bastidor NS.:' + bastidor)
				print('			' + module)
				for aux_current in SetCurrentList:
					drs.SetISlowRefx4(aux_current, aux_current, test_current, aux_current)
					time.sleep(0.5)
					print('Modulo 1: ' + str(drs.Read_iMod1()))
					time.sleep(0.5)
					print('Modulo 2: ' + str(drs.Read_iMod2()))
					time.sleep(0.5)
					print('Modulo 3: ' + str(drs.Read_iMod3()))
					time.sleep(0.5)
					print('Modulo 4: ' + str(drs.Read_iMod4()))
					time.sleep(0.5)
					print('\n')
					time.sleep(StepTime)

		if module_list.index(module) == 3:
			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				drs.SetISlowRefx4(0, 0, 0, test_current)
			time.sleep(WarmUpTime)

			for bastidor in BastidorList:
				drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
				time.sleep(1)
				print('Início de teste:')
				print('			bastidor NS.:' + bastidor)
				print('			' + module)
				for aux_current in SetCurrentList:
					drs.SetISlowRefx4(aux_current, aux_current, aux_current, test_current)
					time.sleep(0.5)
					print('Modulo 1: ' + str(drs.Read_iMod1()))
					time.sleep(0.5)
					print('Modulo 2: ' + str(drs.Read_iMod2()))
					time.sleep(0.5)
					print('Modulo 3: ' + str(drs.Read_iMod3()))
					time.sleep(0.5)
					print('Modulo 4: ' + str(drs.Read_iMod4()))
					time.sleep(0.5)
					print('\n')
					time.sleep(StepTime)

for bastidor in BastidorList:
	drs.SetSlaveAdd(BastidorList.index(bastidor) + 1)
	time.sleep(1)
	drs.TurnOff(0b1111)

print(str(now.day) + ',' + str(now.hour) + ':' + str(now.minute))
#########################################################################

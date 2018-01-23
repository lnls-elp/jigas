#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 22/06/2016
Versão 1.0
@author: Heitor/Ricieri (ELP)
Python 3.4.4
"""

import time
import visa

class DSOX_3024A_USB(object):

	def __init__(self):
		#self.rm = visa.ResourceManager('@py') #Using PyVisa-py backend
		self.rm = visa.ResourceManager()

	def connect(self,visa_address):
		self.inst = self.rm.open_resource(visa_address)
		del self.inst.timeout


	def get_setup(self):
		self.inst.write(':SYSTem:SETup?')
		return self.inst.read_raw()


	def setup_config(self,file_name):
		file = open(file_name, 'r')
		data = file.read()
		file.close()
		self.inst.write(':SYSTem:SETup ' + data)


	def timebase_get(self):
		return self.inst.query(':TIMebase:SCALe?')


	def timebase_set(self, TimeBase):
		self.inst.write(':TIMebase:SCALe ' + str(TimeBase))


	def standard_scale(self):
		self.inst.write(':CHANnel1:COUPling AC')
		self.inst.write(':CHANnel1:Scale 0.02V')
		self.inst.write(':CHANnel1:OFFSet -0.055V')

		self.inst.write(':CHANnel2:COUPling AC')
		self.inst.write(':CHANnel2:Scale 0.05V')
		self.inst.write(':CHANnel2:OFFSet -0.035V')

		self.inst.write(':CHANnel3:COUPling AC')
		self.inst.write(':CHANnel3:Scale 1V')
		self.inst.write(':CHANnel3:OFFSet 1.5V')

		time.sleep(1)

	def auto_scale(self, nChannels):
		for i in range(1, nChannels + 1):
			self.inst.write(':CHANnel'+str(i)+':COUPling AC')
			self.inst.write(':CHANnel'+str(i)+':SCAle 1V')
			self.inst.write(':CHANnel'+str(i)+':OFFSet 0')

		for j in range(1, nChannels + 1):
			self.inst.write(':RUN')
			ch_vpp = 5
			trigger_status = False

			while ch_vpp >= 5:
				for k in range(0,3):
					self.inst.write(':MEASure:SOURce CHANnel'+str(j))
					time.sleep(1)
					#print(self.inst.query(':MEASure:VPP?'))
					ch_vpp = self.inst.query(':MEASure:VPP?')
					ch_vpp = float(ch_vpp)/2
					time.sleep(1)
					WriteString = ':CHANnel'+str(j)+':SCALe '+str(ch_vpp)
					self.inst.write(WriteString)
					time.sleep(2)

			while trigger_status != True:
				self.inst.write('*CLS')  # clears the status data structures, the device-defined error queue,
							 # and the Request-for-OPC flag
				self.inst.write(':SINGle')
				time.sleep(float(self.timebase_get())*11)
				self.inst.write(':TER?')  # reads the Trigger Event Register
				trigger_status = int(self.inst.read())
				time.sleep(1)

			vpp_list = []
			scale_list = []

		for l in range(0, nChannels):
			self.inst.write(':MEASure:SOURce CHANnel' + str(l+1))
			vpp_list.append(float(self.inst.query(':MEASure:VPP?')))
			scale_list.append(float(self.inst.query(':CHANnel'+str(l+1)+':SCALe?')))

		for m in range(1, nChannels + 1):
			offset = str(((m*2)-5) * scale_list[m-1])
			WriteString = ':CHANnel' + str(m) + ':OFFSet ' + offset  + 'V'
			self.inst.write(WriteString)
			time.sleep(1)


	def single_shot(self,nShots,nChannels):
		MeasureList = []

		self.inst.write(':RUN')

		for i in range(0,nShots,1):
			self.inst.write(':SINGle')
			time.sleep(1.5)

			if (i == 0):
				for a in range(1, nChannels + 1):
					self.inst.write(':MEASure:SOURce CHANnel' + str(a))
					time.sleep(1)
					MeasureList.append(float(self.inst.query(':MEASure:VPP?')))
					time.sleep(1)
			else:
				for b in range(1, nChannels + 1):
					self.inst.write(':MEASure:SOURce CHANnel' + str(b))
					time.sleep(1)
					MeasureList[b-1] = MeasureList[b-1] + float(self.inst.query('MEASure:VPP?'))
					time.sleep(1)
					#MeasureList.append(float(self.inst.query(':MEASure:VPP?')))
					#time.sleep(1)

		for j in range(0,len(MeasureList),1):
			MeasureList[j] = MeasureList[j]/nShots

		return MeasureList


	def get_results(self, nChannels, FileName):
		self.inst.write(':STOP')

		MeasureList = []

		Measurements = self.inst.query(':MEASure:RESults?')
		Measurements = Measurements.split(',')

		a = 4

		for b in range(0, nChannels):
			MeasureList.append(float(Measurements[a]))
			a = a + 7

		self.inst.write(':SAVE:IMAGe:FORMat PNG')
		self.inst.write(':SAVE:IMAGe:STARt "' + FileName + '"')

		time.sleep(6)

		return MeasureList

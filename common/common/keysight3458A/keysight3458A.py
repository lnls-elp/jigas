#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 20/03/2017
Versão 1.0
@author: Gabriel (ELP)
Python 3.4
"""

import struct
import glob
import serial
import time
import visa
import csv

from datetime import datetime

class Keysight3458A_GPIB(object):

    def __init__(self):
        self.rm = visa.ResourceManager()

    def Connect(self,select_instru = 'GPIB0::22::INSTR'):
        self.inst = self.rm.open_resource(select_instru)
        self.inst.clear()
        self.inst.timeout = 10000
        #self.inst.read_termination = '\r'
        self.inst.read_termination = '\r\n'
        self.inst.write('RESET')
        #self.inst.write('PRESET NORM;INBUF OFF;CSB;DELAY -1;MEM FIFO;TBUFF ON;NPLC 10;NDIG 8;END 2;TARM AUTO;TRIG AUTO')
        self.inst.write('PRESET NORM;MFORMAT DREAL;OFORMAT ASCII;INBUF OFF;CSB;DELAY -1;MEM OFF;TBUFF ON;NPLC 10;NDIG 8;END 0;TRIG AUTO')


    def InitDefault(self):
        self.inst.write('PRESET NORM;MFORMAT DREAL;OFORMAT ASCII;INBUF OFF;CSB;DELAY -1;MEM OFF;TBUFF ON;NPLC 10;NDIG 8;END 0;TRIG AUTO')

    def SetMeasurementType(self,inputType,inputRange = ''):
        self.inst.write('TRIG HOLD;' + inputType + ' ' + str(inputRange) + ';TRIG AUTO')

    def SetMultipointMeas(self,sampleCount = 10,trigType = 'AUTO'):
        #self.inst.write('TARM HOLD;TRIG ' + trigType + ';NRDGS ' + str(sampleCount) + ',AUTO;MEM FIFO')
        self.inst.write('TARM HOLD;TRIG ' + trigType + ';NRDGS ' + str(sampleCount) + ',AUTO;MEM FIFO')

    def GetLastMeasurement(self):
        return float(self.inst.read())

    def TrigMultipointMeas(self,tarmcount = 1):
        self.inst.write('MEM FIFO;TARM SGL,' + str(tarmCount))

    def GetMultipointMeas(self):
        return float(self.inst.read())
        count = self.inst.query('MCOUNT?')
        self.inst.write('RMEM 1,' + count)
        while(not self.inst.stb & 0x80):
            pass
        return [float(val) for val in self.inst.read().split(',')]

    def ReadMeasurementPoints(self,tarmCount = 1):
        #count = self.inst.query('MEM FIFO;TARM SGL,' + str(trigCount) + ';MEM OFF;MATH OFF;MMATH OFF;MCOUNT?')
        #self.inst.write('MEM CONT;RMEM 1,' + count)
        count = self.inst.query('MEM FIFO;TARM SGL,' + str(tarmCount) + ';MCOUNT?')
        self.inst.write('RMEM 1,' + count)
        while(not self.inst.stb & 0x80):
            pass
        return [float(val) for val in self.inst.read().split(',')]

if __name__ == '__main__':
    DMM = Keysight3458A_GPIB()
    DMM.Connect()


'''

>>> ================================ RESTART ================================
>>>
>>> DMM.inst.write('TARM SGL')
(10, <StatusCode.success: 0>)
>>> DMM.inst.query('MCOUNT?')
'5'
>>> DMM.inst.write('RMEM 1,5')
(10, <StatusCode.success: 0>)
>>> DMM.inst.read_termination = None
>>> DMM.inst.read_raw()
b'@#\xff\xfe:wTc'
>>> DMM.inst.read_raw()
b'@#\xff\xfe(\x80\xa9\x88'
>>> DMM.inst.read_raw()
b'@#\xff\xfe;\x10\x9eY'
>>> DMM.inst.read_raw()
b'@#\xff\xfe\x18\xef&\x86'
>>> DMM.inst.read_raw()
b'@#\xff\xfeM\x07I4'
>>> DMM.inst.read_raw()
Traceback (most recent call last):
  File "<pyshell#258>", line 1, in <module>
    DMM.inst.read_raw()
  File "C:\Python34\lib\site-packages\pyvisa\resources\messagebased.py", line 306, in read_raw
    chunk, status = self.visalib.read(self.session, size)
  File "C:\Python34\lib\site-packages\pyvisa\ctwrapper\functions.py", line 1582, in read
    ret = library.viRead(session, buffer, count, byref(return_count))
  File "C:\Python34\lib\site-packages\pyvisa\ctwrapper\highlevel.py", line 188, in _return_handler
    raise errors.VisaIOError(ret_value)
pyvisa.errors.VisaIOError: VI_ERROR_TMO (-1073807339): Timeout expired before operation completed.
'''

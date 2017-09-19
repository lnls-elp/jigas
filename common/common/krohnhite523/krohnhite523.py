#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 20/09/2016
Versão 1.0
@author: Ricieri (ELP)
Python 3.4.4
"""

import struct
import glob
import serial
import time
import visa
import csv

from datetime import datetime

class KrohnHite523_GPIB(object):

    def __init__(self):
        self.rm = visa.ResourceManager()

    def IDN(self):
        idn_string = self.inst.query('*IDN?')
        return idn_string

    def Reset(self):
        self.inst.write('*RST')

    def EnableOutput(self):
        new_string = 'V'
        self.inst.write(new_string)

    def DisableOutput(self):
        new_string = 'Z'
        self.inst.write(new_string)

    def DeltaIncrement(self):
        delta_value_string = 'D'
        self.inst.write(delta_value_string)

    def DeltaDecrement(self):
        delta_value_string = '-D'
        self.inst.write(delta_value_string)

    def SetVoltageOutput(self,voltage_level,scale):
        voltage_level_string = str(voltage_level)+scale
        self.inst.write(voltage_level_string)

    def SetCurrentOutput(self,current_level,scale):
        current_level_string = str(current_level)+scale
        self.inst.write(current_level_string)

    def SetOutput(self,level,mode):
        string = ''
        if(mode == 'V'):
            string = str(level) + 'V' if abs(level) > 1e-6 else str(level*1e6) + 'uV'
        elif(mode == 'I'):
            string = str(level*1e3) + 'mA'
        print(string)
        self.inst.write(string)

    def SetVoltageLimit(self,voltage_limit):
        voltage_limit_string = str(round(abs(voltage_limit)))+'C'
        self.inst.write(voltage_limit_string)

    def OutputTermination(self,output_termination):
        if output_termination == 0:
            output_termination_string = '2W'
        else:
            output_termination_string = '4W'
        self.inst.write(output_termination_string)

    def LOFloatChassis(self,lo_float):
        if lo_float == 0:
            lo_float_chassis_string = 'F'
        else:
            lo_float_chassis_string = 'G'
        self.inst.write(lo_float_chassis_string)

    def SetVoltageDelta(self,voltage_delta,scale):
        voltage_delta_string = str(voltage_delta)+scale
        self.inst.write(voltage_delta_string)

    def SetCurrentDelta(self,current_delta,scale):
        current_delta_string = str(current_delta)+scale
        self.inst.write(current_delta_string)

    def STG(self):
        string = self.inst.query('*STG?')
        return string

    def Connect(self,gpibAdd):
        self.inst = self.rm.open_resource(gpibAdd)
        self.inst.timeout = 5000
        #self.inst.write('Z;F')

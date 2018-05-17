#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on 26/04/2016
Versão 1.0
@author: Ricieri (ELP)
Python 3.4.4
"""

import struct
import glob
import serial
import time
import csv
import math
import numpy as np

from datetime import datetime

'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
======================================================================
                    Listas de Entidades BSMP
        A posição da entidade na lista corresponde ao seu ID BSMP
======================================================================
'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

ListVar = ['iLoad1','iLoad2','iMod1','iMod2','iMod3','iMod4','vLoad',
           'vDCMod1','vDCMod2','vDCMod3','vDCMod4','vOutMod1','vOutMod2',
           'vOutMod3','vOutMod4','temp1','temp2','temp3','temp4','ps_OnOff',
           'ps_OpMode','ps_Remote','ps_OpenLoop','ps_SoftInterlocks',
           'ps_HardInterlocks','iRef','wfmRef_Gain','wfmRef_Offset','sigGen_Enable','sigGen_Type',
           'sigGen_Ncycles','sigGenPhaseStart','sigGen_PhaseEnd','sigGen_Freq',
           'sigGen_Amplitude','sigGen_Offset','sigGen_Aux','dp_ID','dp_Class','dp_Coeffs','ps_Model',
           'wfmRef_PtrBufferStart','wfmRef_PtrBufferEnd','wfmRef_PtrBufferK','wfmRef_SyncMode']
ListCurv = ['wfmRef_Curve','sigGen_SweepAmp','samplesBuffer','fullwfmRef_Curve','wfmRef_Blocks','samplesBuffer_blocks']
ListFunc = ['TurnOn','TurnOff','OpenLoop','ClosedLoop','OpMode','RemoteInterface',
            'SetISlowRef','ConfigWfmRef','ConfigSigGen', 'EnableSigGen',
            'DisableSigGen','ConfigDPModule','WfmRefUpdate','ResetInterlocks','ConfigPSModel',
            'ConfigHRADC','ConfigHRADCOpMode','EnableHRADCSampling','DisableHRADCSampling','ResetWfmRef',
            'SetRSAddress','EnableSamplesBuffer','DisableSamplesBuffer','SetISlowRefx4','SelectHRADCBoard','SelectTestSource',
            'ResetHRADCBoards','Config_nHRADC','ReadHRADC_UFM','WriteHRADC_UFM','EraseHRADC_UFM','ReadHRADC_BoardData']
ListTestFunc = ['UdcIoExpanderTest', 'UdcLedTest', 'UdcBuzzerTest', 'UdcEepromTest', 'UdcFlashTest', 'UdcRamTest',
                'UdcRtcTest', 'UdcSensorTempTest', 'UdcIsoPlaneTest', 'UdcAdcTest', 'UdcUartTest', 'UdcLoopBackTest',
                'UdcComTest', 'UdcI2cIsoTest']
ListHRADCInputType = ['Vin_bipolar','Vin_unipolar_p','Vin_unipolar_n','Iin_bipolar','Iin_unipolar_p',
                      'Iin_unipolar_n','Vref_bipolar_p','Vref_bipolar_n','GND','Vref_unipolar_p',
                      'Vref_unipolar_n','GND_unipolar','Temp','Reserved0','Reserved1','Reserved2']

ListPSModels = ['FBP_100kHz', 'FBP_Parallel_100kHz', 'FAC_ACDC_10kHz', 'FAC_DCDC_20kHz',
                'FAC_Full_ACDC_10kHz', 'FAC_Full_DCDC_20kHz', 'FAP_ACDC',
                'FAP_DCDC_20kHz', 'TEST_HRPWM', 'TEST_HRADC', 'JIGA_HRADC',
                'FAP_DCDC_15kHz_225A', 'FBPx4_100kHz', 'FAP_6U_DCDC_20kHz',
                'JIGA_BASTIDOR']

ListPSModels_v2_1 = ['Empty','FBP','FBP_DCLink','FAC_ACDC','FAC_DCDC']
ListVar_v2_1 = ['ps_status','ps_setpoint','ps_reference','firmware_version',
                'counter_set_slowref','counter_sync_pulse','siggen_enable',
                'siggen_type','siggen_num_cycles','siggen_n','siggen_freq',
                'siggen_amplitude','siggen_offset','siggen_aux_param',
                'wfmref_selected','wfmref_sync_mode','wfmref_gain',
                'wfmref_offset','p_wfmref_start','p_wfmref_end','p_wfmref_idx']

ListFunc_v2_1 = ['turn_on','turn_off','open_loop','closed_loop','select_op_mode',
                 'select_ps_model','reset_interlocks','remote_interface',
                 'set_serial_address','set_serial_termination','unlock_udc',
                 'lock_udc','cfg_buf_samples','enable_buf_samples',
                 'disable_buf_samples','sync_pulse','set_slowref',
                 'set_slowref_fbp','reset_counters','scale_wfmref',
                 'select_wfmref','save_wfmref','reset_wfmref','cfg_siggen',
                 'set_siggen','enable_siggen','disable_siggen','set_slowref_readback',
                 'set_slowref_fbp_readback','set_param','get_param',
                 'save_param_eeprom','load_param_eeprom', 'save_param_bank',
                 'load_param_bank','set_dsp_coeffs','get_dsp_coeff',
                 'save_dsp_coeffs_eeprom', 'load_dsp_coeffs_eeprom',
                 'save_dsp_modules_eeprom', 'load_dsp_modules_eeprom','reset_udc']

ListOpMode_v2_1 = ['Off','Interlock','Initializing','SlowRef','SlowRefSync',
                   'Cycle','RmpWfm','MigWfm','FastRef']

ListParameters = ['PS_Name','PS_Model','Num_PS_Modules','Command_Interface',
                  'RS485_Baudrate','RS485_Address','RS485_Termination',
                  'UDCNet_Address','Ethernet_IP','Ethernet_Subnet_Mask',
                  'Freq_ISR_Controller','Freq_TimeSlicer','Max_Ref','Min_Ref',
                  'Max_Ref_OpenLoop','Min_Ref_OpenLoop','Max_SlewRate_SlowRef',
                  'Max_SlewRate_SigGen_Amp','Max_SlewRate_SigGen_Offset',
                  'Max_SlewRate_WfmRef','PWM_Freq','PWM_DeadTime',
                  'PWM_Max_Duty','PWM_Min_Duty','PWM_Max_Duty_OpenLoop',
                  'PWM_Min_Duty_OpenLoop','PWM_Lim_Duty_Share',
                  'HRADC_Num_Boards','HRADC_Freq_SPICLK','HRADC_Freq_Sampling',
                  'HRADC_Enable_Heater','HRADC_Enable_Monitor',
                  'HRADC_Type_Transducer','HRADC_Gain_Transducer',
                  'HRADC_Offset_Transducer','SigGen_Type','SigGen_Num_Cycles',
                  'SigGen_Freq','SigGen_Amplitude','SigGen_Offset',
                  'SigGen_Aux_Param','WfmRef_ID_WfmRef','WfmRef_SyncMode',
                  'WfmRef_Gain','WfmRef_Offset','Analog_Var_Max','Analog_Var_Min']


ListBCBFunc = ['ClearPof', 'SetPof', 'ReadPof', 'EnableBuzzer', 'DisableBuzzer',
                'SendUartData', 'GetUartData', 'SendCanData', 'GetCanData',
                'GetI2cData']

typeFormat = {'uint8_t': 'BBHBB', 'uint16_t': 'BBHHB', 'uint32_t': 'BBHIB',
              'float': 'BBHfB'}
bytesFormat = {'Uint16': 'H', 'Uint32': 'L', 'Uint64': 'Q', 'float': 'f'}

typeSize   = {'uint8_t': 6, 'uint16_t': 7, 'uint32_t': 9, 'float': 9}
ufmOffset = {'serial': 0, 'calibdate': 4, 'variant': 9, 'rburden': 10,
             'calibtemp': 12, 'vin_gain': 14, 'vin_offset': 16,
             'iin_gain': 18, 'iin_offset': 20, 'vref_p': 22, 'vref_n': 24,
             'gnd': 26}
hradcVariant = ['HRADC-FBP','HRADC-FAX-A','HRADC-FAX-B','HRADC-FAX-C','HRADC-FAX-D']
hradcInputTypes = ['GND', 'Vref_bipolar_p', 'Vref_bipolar_n', 'Temp',
                       'Vin_bipolar_p', 'Vin_bipolar_n', 'Iin_bipolar_p','Iin_bipolar_n']

NUM_MAX_COEFFS_DSP = 12

class SerialDRS(object):

    ser = serial.Serial()

    def __init__(self):
        #self.ser=serial.Serial()
        self.MasterAdd              = '\x00'
        self.SlaveAdd               = '\x01'
        self.BCastAdd               = '\xFF'
        self.ComWriteVar            = '\x20'
        self.WriteFloatSizePayload  = '\x00\x05'
        self.WriteDoubleSizePayload = '\x00\x03'
        self.ComReadVar             = '\x10\x00\x01'
        self.ComRequestCurve        = '\x40'
        self.ComSendWfmRef          = '\x41'
        self.ComFunction            = '\x50'

        self.DP_MODULE_MAX_COEFF    = 16

        self.ListDPClass = ['ELP_Error','ELP_SRLim','ELP_LPF','ELP_PI_dawu','ELP_IIR_2P2Z','ELP_IIR_3P3Z',
                            'DCL_PID','DCL_PI','DCL_DF13','DCL_DF22','DCL_23']
        self.ListHardInterlocks = ['Sobrecorrente', 'Interlock Externo', 'Falha AC',
                               'Falha ACDC', 'Falha DCDC','Sobretensao','Falha Resistor Precarga','Falha Carga Capacitores Saída',
                               'Botão de Emergência', 'OUT_OVERVOLTAGE', 'IN_OVERVOLTAGE','ARM1_OVERCURRENT','ARM2_OVERCURRENT',
                                'IN_OVERCURRENT','DRIVER1_FAULT','DRIVER2_FAULT','OUT1_OVERCURRENT','OUT2_OVERCURRENT','OUT1_OVERVOLTAGE',
                                'OUT2_OVERVOLTAGE','LEAKAGE_OVERCURRENT','AC_OVERCURRENT']
        self.ListSoftInterlocks = ['IGBT1_OVERTEMP','IGBT2_OVERTEMP','L1_OVERTEMP','L2_OVERTEMP','HEATSINK_OVERTEMP','WATER_OVERTEMP',
                                   'RECTFIER1_OVERTEMP','RECTFIER2_OVERTEMP','AC_TRANSF_OVERTEMP','WATER_FLUX_FAULT','OVER_HUMIDITY_FAULT']

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                    Funções Internas da Classe
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    # Converte float para hexadecimal
    def float_to_hex(self, value):
        hex_value = struct.pack('f', value)
        return hex_value.decode('ISO-8859-1')

    # Converte lista de float  para hexadecimal
    def float_list_to_hex(self, value_list):
        hex_list = b''
        for value in value_list:
            hex_list = hex_list + struct.pack('f', value)
        return hex_list.decode('ISO-8859-1')

    def format_list_size(self, in_list, max_size):
        out_list = in_list[0:max_size]
        if max_size > len(in_list):
            for i in range(max_size - len(in_list)):
                out_list.append(0)
        return out_list

    # Converte double para hexadecimal
    def double_to_hex(self,value):
        hex_value = struct.pack('H',value)
        return hex_value.decode('ISO-8859-1')

    # Converte indice para hexadecimal
    def index_to_hex(self,value):
        hex_value = struct.pack('B',value)
        return hex_value.decode('ISO-8859-1')

    # Converte payload_size para hexadecimal
    def size_to_hex(self,value):
        hex_value = struct.pack('>H',value)
        return hex_value.decode('ISO-8859-1')

    # Função Checksum
    def checksum(self, packet):
        b=bytearray(packet.encode('ISO-8859-1'))
        csum =(256-sum(b))%256
        hcsum = struct.pack('B',csum)
        send_msg = packet + hcsum.decode(encoding='ISO-8859-1')
        return send_msg

    # Função de leitura de variável
    def read_var(self,var_id):
        send_msg = self.checksum(self.SlaveAdd+self.ComReadVar+var_id)
        self.ser.reset_input_buffer()
        self.ser.write(send_msg.encode('ISO-8859-1'))

    def is_open(self):
        return self.ser.isOpen()

    def _convertToUint16List(self, val, format):
        val_16 = []
        val_b = struct.pack(bytesFormat[format],val)
        print(val_b)
        for i in range(0,len(val_b),2):
            val_16.append(struct.unpack('H',val_b[i:i+2])[0])
        print(val_16)
        return val_16

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Chamada de Entidades Funções BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def TurnOn_FAx(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOn'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def TurnOn(self,ps_modules):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_modules
        hex_modules  = self.double_to_hex(ps_modules)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOn'))+hex_modules
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def turn_on(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('turn_on'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        print(send_msg.encode('ISO-8859-1'))
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def TurnOff_FAx(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOff'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def TurnOff(self,ps_modules):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_modules
        hex_modules  = self.double_to_hex(ps_modules)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOff'))+hex_modules
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def turn_off(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('turn_off'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def open_loop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('open_loop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def closed_loop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('closed_loop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def OpenLoop(self,ps_modules):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_modules
        hex_modules  = self.double_to_hex(ps_modules)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('OpenLoop'))+hex_modules
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ClosedLoop(self,ps_modules):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_modules
        hex_modules  = self.double_to_hex(ps_modules)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ClosedLoop'))+hex_modules
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def OpMode(self,op_mode):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_opmode
        hex_opmode   = self.double_to_hex(op_mode)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('OpMode'))+hex_opmode
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def RemoteInterface(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('RemoteInterface'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SetISlowRef(self,setpoint):
        payload_size   = self.size_to_hex(1+4) #Payload: ID + iSlowRef
        hex_setpoint   = self.float_to_hex(setpoint)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SetISlowRef'))+hex_setpoint
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigWfmRef(self,gain,offset):
        payload_size = self.size_to_hex(1+4+4) #Payload: ID + gain + offset
        hex_gain     = self.float_to_hex(gain)
        hex_offset   = self.float_to_hex(offset)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigWfmRef'))+hex_gain+hex_offset
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigSigGen(self,sigType,nCycles,phaseStart,phaseEnd):
        payload_size   = self.size_to_hex(1+2+2+4+4) #Payload: ID + type + nCycles + phaseStart + phaseEnd
        hex_sigType    = self.double_to_hex(sigType)
        hex_nCycles    = self.double_to_hex(nCycles)
        hex_phaseStart = self.float_to_hex(phaseStart)
        hex_phaseEnd   = self.float_to_hex(phaseEnd)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigSigGen'))+hex_sigType+hex_nCycles+hex_phaseStart+hex_phaseEnd
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EnableSigGen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('EnableSigGen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def DisableSigGen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('DisableSigGen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigDPModule(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigDPModule'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigDPModuleFull(self,dp_id,dp_class,dp_coeffs):
        self.Write_dp_ID(dp_id)
        self.Write_dp_Class(dp_class)
        self.Write_dp_Coeffs(dp_coeffs)
        self.ConfigDPModule()

    def WfmRefUpdate(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('WfmRefUpdate'))
        send_msg     = self.checksum(self.BCastAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))

    def ResetInterlocks(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ResetInterlocks'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def reset_interlocks(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('reset_interlocks'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigPSModel(self,ps_model):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_Model
        hex_model    = self.double_to_hex(ps_model)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigPSModel'))+hex_model
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigHRADC(self,hradcID,freqSampling,inputType,enableHeater,enableMonitor):
        payload_size   = self.size_to_hex(1+2+4+2+2+2) #Payload: ID + hradcID + freqSampling + inputType + enableHeater + enableMonitor
        hex_hradcID    = self.double_to_hex(hradcID)
        hex_freq       = self.float_to_hex(freqSampling)
        hex_type       = self.double_to_hex(ListHRADCInputType.index(inputType))
        hex_enHeater   = self.double_to_hex(enableHeater)
        hex_enMonitor  = self.double_to_hex(enableMonitor)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigHRADC'))+hex_hradcID+hex_freq+hex_type+hex_enHeater+hex_enMonitor
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ConfigHRADCOpMode(self,hradcID,opMode):
        payload_size   = self.size_to_hex(1+2+2) #Payload: ID + hradcID + opMode
        hex_hradcID    = self.double_to_hex(hradcID)
        hex_opMode     = self.double_to_hex(opMode)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ConfigHRADCOpMode'))+hex_hradcID+hex_opMode
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EnableHRADCSampling(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('EnableHRADCSampling'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def DisableHRADCSampling(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('DisableHRADCSampling'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ResetWfmRef(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ResetWfmRef'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SetRSAddress(self,rs_address):
        payload_size = self.size_to_hex(1+2) #Payload: ID + rs_address
        hex_add = self.double_to_hex(rs_address)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SetRSAddress'))+hex_add
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EnableSamplesBuffer(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('EnableSamplesBuffer'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def DisableSamplesBuffer(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('DisableSamplesBuffer'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SelectHRADCBoard(self,hradcID):
        payload_size   = self.size_to_hex(1+2) #Payload: ID
        hex_hradcID    = self.double_to_hex(hradcID)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SelectHRADCBoard'))+hex_hradcID
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SelectTestSource(self,inputType):
        payload_size   = self.size_to_hex(1+2) #Payload: inputType
        hex_type       = self.double_to_hex(ListHRADCInputType.index(inputType))
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SelectTestSource'))+hex_type
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ResetHRADCBoards(self, enable):
        payload_size   = self.size_to_hex(1+2) #Payload: ID+enable(2)
        hex_enable     = self.double_to_hex(enable)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ResetHRADCBoards'))+hex_enable
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def Config_nHRADC(self,nHRADC):
        payload_size   = self.size_to_hex(1+2) #Payload: nHRADC
        hex_nhradc     = self.double_to_hex(nHRADC)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('Config_nHRADC'))+hex_nhradc
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ReadHRADC_UFM(self,hradcID,ufmadd):
        payload_size   = self.size_to_hex(1+2+2) #Payload: ID + hradcID + ufmadd
        hex_hradcID    = self.double_to_hex(hradcID)
        hex_ufmadd    = self.double_to_hex(ufmadd)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ReadHRADC_UFM'))+hex_hradcID+hex_ufmadd
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def WriteHRADC_UFM(self,hradcID,ufmadd,ufmdata):
        payload_size   = self.size_to_hex(1+2+2+2) #Payload: ID + hradcID + ufmadd + ufmdata
        hex_hradcID    = self.double_to_hex(hradcID)
        hex_ufmadd    = self.double_to_hex(ufmadd)
        hex_ufmdata    = self.double_to_hex(ufmdata)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('WriteHRADC_UFM'))+hex_hradcID+hex_ufmadd+hex_ufmdata
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EraseHRADC_UFM(self,hradcID):
        payload_size   = self.size_to_hex(1+2) #Payload: ID + hradcID
        hex_hradcID    = self.double_to_hex(hradcID)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('EraseHRADC_UFM'))+hex_hradcID
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def InitHRADC_BoardData(self, serial = 12345678, day = 1, mon = 1,
                            year = 2017, hour = 12, minutes = 30,
                            variant = 'HRADC-FBP', rburden = 20, calibtemp = 40,
                            vin_gain = 1, vin_offset = 0, iin_gain = 1,
                            iin_offset = 0, vref_p = 5, vref_n = -5, gnd = 0):
        boardData = {'serial': serial, 'variant': variant, 'rburden': rburden,
                     'tm_mday': day, 'tm_mon': mon, 'tm_year': year,
                     'tm_hour': hour, 'tm_min': minutes, 'calibtemp': calibtemp,
                     'vin_gain': vin_gain, 'vin_offset': vin_offset,
                     'iin_gain': iin_gain, 'iin_offset': iin_offset,
                     'vref_p': vref_p, 'vref_n': vref_n, 'gnd': gnd}
        return boardData

    def WriteHRADC_BoardData(self,hradcID,boardData):
        print('Configurando placa em UFM mode...')
        self.ConfigHRADCOpMode(hradcID,1)
        time.sleep(0.5)

        print('\nEnviando serial number...')
        ufmdata_16 = self._convertToUint16List(boardData['serial'],'Uint64')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['serial'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando variante...')
        ufmdata_16 = self._convertToUint16List(hradcVariant.index(boardData['variant']),'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['variant'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando rburden...')
        ufmdata_16 = self._convertToUint16List(boardData['rburden'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['rburden'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando calibdate...')
        ufmdata_16 = self._convertToUint16List(boardData['tm_mday'],'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibdate'],ufmdata_16[i])
            time.sleep(0.1)
        # Month
        ufmdata_16 = self._convertToUint16List(boardData['tm_mon'],'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibdate']+1,ufmdata_16[i])
            time.sleep(0.1)
        # Year
        ufmdata_16 = self._convertToUint16List(boardData['tm_year'],'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibdate']+2,ufmdata_16[i])
            time.sleep(0.1)
        # Hour
        ufmdata_16 = self._convertToUint16List(boardData['tm_hour'],'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibdate']+3,ufmdata_16[i])
            time.sleep(0.1)
        # Minutes
        ufmdata_16 = self._convertToUint16List(boardData['tm_min'],'Uint16')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibdate']+4,ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando calibtemp...')
        ufmdata_16 = self._convertToUint16List(boardData['calibtemp'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['calibtemp'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando vin_gain...')
        ufmdata_16 = self._convertToUint16List(boardData['vin_gain'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['vin_gain'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando vin_offset...')
        ufmdata_16 = self._convertToUint16List(boardData['vin_offset'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['vin_offset'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando iin_gain...')
        ufmdata_16 = self._convertToUint16List(boardData['iin_gain'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['iin_gain'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando iin_offset...')
        ufmdata_16 = self._convertToUint16List(boardData['iin_offset'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['iin_offset'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando vref_p...')
        ufmdata_16 = self._convertToUint16List(boardData['vref_p'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['vref_p'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando vref_n...')
        ufmdata_16 = self._convertToUint16List(boardData['vref_n'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['vref_n'],ufmdata_16[i])
            time.sleep(0.1)

        print('\nEnviando gnd...')
        ufmdata_16 = self._convertToUint16List(boardData['gnd'],'float')
        for i in range(len(ufmdata_16)):
            self.WriteHRADC_UFM(hradcID,i+ufmOffset['gnd'],ufmdata_16[i])
            time.sleep(0.1)

        print('Colocando a placa em Sampling mode...')
        self.ConfigHRADCOpMode(hradcID,0)

    def ReadHRADC_BoardData(self,hradcID):
        print('Configurando placa em UFM mode...')
        print(self.ConfigHRADCOpMode(hradcID,1))
        time.sleep(0.5)

        print('Extraindo dados da placa...')
        payload_size   = self.size_to_hex(1+2) #Payload: ID + hradcID
        hex_hradcID    = self.double_to_hex(hradcID)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ReadHRADC_BoardData'))+hex_hradcID
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        print(self.ser.read(6))

        print('Lendo dados da placa...')
        self.read_var(self.index_to_hex(50+hradcID))
        reply_msg = self.ser.read(1+1+2+56+1)
        print(reply_msg)
        print(len(reply_msg))
        val = struct.unpack('BBHLLHHHHHHfffffffffB',reply_msg)
        print(val)
        boardData = self.InitHRADC_BoardData(val[3]+val[4]*pow(2,32),val[5],
                                             val[6],val[7],val[8],val[9],
                                             hradcVariant[val[10]],val[11],
                                             val[12],val[13],val[14],val[15],
                                             val[16],val[17],val[18],val[19])

        print('Colocando a placa em Sampling mode...')
        print(self.ConfigHRADCOpMode(hradcID,0))
        time.sleep(0.5)

        return boardData

    def UpdateHRADC_BoardData(self,hradcID):
        variant = len(hradcVariant)
        while variant >= len(hradcVariant) or variant < 0:
            variant = int(input("Enter HRADC variant number:\n  0: HRADC-FBP\n  1: HRADC-FAX-A\n  2: HRADC-FAX-B\n  3: HRADC-FAX-C\n  4: HRADC-FAX-D\n\n>>> "))
        variant = hradcVariant[variant]

        boardData = self.ReadHRADC_BoardData(hradcID)
        boardData['variant'] = variant
        boardData['vin_offset'] = np.float32(0)
        boardData['iin_offset'] = np.float32(0)

        if variant == 'HRADC-FAX-A':
            boardData['rburden'] = np.float32(0)
            boardData['vin_gain'] = np.float32(5.0/6.0)
            boardData['iin_gain'] = np.float32(5.0/6.0)
            print(boardData['vin_gain'])
            print(boardData['variant'])

        elif variant == 'HRADC-FAX-B':
            boardData['rburden'] = np.float32(0)
            boardData['vin_gain'] = np.float32(1)
            boardData['iin_gain'] = np.float32(1)
            print(boardData['vin_gain'])
            print(boardData['variant'])

        elif variant == 'HRADC-FAX-C':
            boardData['rburden'] = np.float32(5)
            boardData['vin_gain'] = np.float32(1)
            boardData['iin_gain'] = np.float32(1)
            print(boardData['vin_gain'])
            print(boardData['variant'])

        elif variant == 'HRADC-FAX-D':
            boardData['rburden'] = np.float32(1)
            boardData['vin_gain'] = np.float32(1)
            boardData['iin_gain'] = np.float32(1)
            print(boardData['vin_gain'])
            print(boardData['variant'])

        print('\n\nBoard data from HRADC of slot #' + str(hradcID) + ' is about to be overwritten by the following data:')
        print(boardData)

        i = input('\n Do you want to proceed? [y/n]: ')

        if i is 'Y' or i is 'y':
            self.ConfigHRADCOpMode(hradcID,1)
            time.sleep(0.1)
            self.EraseHRADC_UFM(hradcID)
            time.sleep(0.5)
            self.ResetHRADCBoards(1)
            time.sleep(0.5)
            self.ResetHRADCBoards(0)
            time.sleep(1.5)
            self.WriteHRADC_BoardData(hradcID,boardData)
            boardData_new = self.ReadHRADC_BoardData(hradcID)
            print(boardData_new)
            print(boardData)
            if boardData_new == boardData:
                print('\n\n ### Operation was successful !!! ### \n\n')
            else:
                print('\n\n ### Operation failed !!! ### \n\n')

        return [boardData, boardData_new]

    def GetHRADCs_BoardData(self,numHRADC):
        boardData_list = []
        for i in range(numHRADC):
            boardData_list.append(self.ReadHRADC_BoardData(i))
        return boardData_list

    def UdcEepromTest(self, rw, data=None):
        if data is not None:
            payload_size    = self.size_to_hex(12)
            hex_rw          = self.double_to_hex(rw)
            hex_byte_0      = self.double_to_hex(data[0])
            hex_byte_1      = self.double_to_hex(data[1])
            hex_byte_2      = self.double_to_hex(data[2])
            hex_byte_3      = self.double_to_hex(data[3])
            hex_byte_4      = self.double_to_hex(data[4])
            hex_byte_5      = self.double_to_hex(data[5])
            hex_byte_6      = self.double_to_hex(data[6])
            hex_byte_7      = self.double_to_hex(data[7])
            hex_byte_8      = self.double_to_hex(data[8])
            hex_byte_9      = self.double_to_hex(data[9])
            send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcEepromTest'))+hex_rw[0]+ \
                                hex_byte_0[0] + hex_byte_1[0] + hex_byte_2[0] + hex_byte_3[0] + hex_byte_4[0] + hex_byte_5[0]+ \
                                hex_byte_6[0] + hex_byte_7[0] + hex_byte_8[0] + hex_byte_9[0]

            print(send_packet.encode('ISO-8859-1'))
            self.ser.write(send_packet.encode('ISO-8859-1'))
            return self.ser.read(15)

    def UdcFlashTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcFlashTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcRamTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcRamTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcAdcTest(self, rw, channel):
        payload_size    = self.size_to_hex(3)
        hex_rw          = self.double_to_hex(rw)
        hex_channel     = self.double_to_hex(channel)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcAdcTest'))+hex_rw[0]+hex_channel[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcSensorTempTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcSensorTempTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcRtcTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcRtcTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcUartTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcUartTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcIoExpanderTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcIoExpanderTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

#    def UdcEthernetTest(self, rw):
#        payload_size    = self.size_to_hex(2)
#        hex_rw          = self.double_to_hex(rw)
#        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcEthernetTest'))+hex_rw
#        self.ser.write(send_packet.encode('ISO-8859-1'))
#        return self.ser.read()

    def UdcIsoPlaneTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcIsoPlaneTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcLoopBackTest(self, rw, channel):
        payload_size    = self.size_to_hex(3)
        hex_rw          = self.double_to_hex(rw)
        hex_channel     = self.double_to_hex(channel)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcLoopBackTest'))+hex_rw[0]+hex_channel[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcLedTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcLedTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcBuzzerTest(self, rw):
        payload_size    = self.size_to_hex(2)
        hex_rw          = self.double_to_hex(rw)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcBuzzerTest'))+hex_rw[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def UdcComTest(self, rw, val):
        payload_size    = self.size_to_hex(3)
        hex_rw          = self.double_to_hex(rw)
        hex_value       = self.double_to_hex(val)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcComTest'))+hex_rw[0]+hex_value[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        time.sleep(0.2)
        return self.ser.read(6)

    def UdcI2cIsoTest(self, rw, val):
        payload_size    = self.size_to_hex(3)
        hex_rw          = self.double_to_hex(rw)
        hex_value       = self.double_to_hex(val)
        send_packet     = self.ComFunction+payload_size+self.index_to_hex(ListTestFunc.index('UdcI2cIsoTest'))+hex_rw[0]+hex_value[0]
        self.ser.write(send_packet.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SetISlowRefx4(self, iRef1 = 0, iRef2 = 0, iRef3 = 0, iRef4 = 0):
        payload_size = self.size_to_hex(1+4*4) #Payload: ID + 4*iRef
        hex_iRef1    = self.float_to_hex(iRef1)
        hex_iRef2    = self.float_to_hex(iRef2)
        hex_iRef3    = self.float_to_hex(iRef3)
        hex_iRef4    = self.float_to_hex(iRef4)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('SetISlowRefx4'))+hex_iRef1+hex_iRef2+hex_iRef3+hex_iRef4
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SetPof(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('SetPof'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ClearPof(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('ClearPof'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def ReadPof(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('ReadPof'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def EnableBuzzer(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('EnableBuzzer'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def DisableBuzzer(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('DisableBuzzer'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SendUartData(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('SendUartData'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def GetUartData(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('GetUartData'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def SendCanData(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('SendCanData'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def GetCanData(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('GetCanData'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def GetI2cData(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListBCBFunc.index('GetI2cData'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def read_ps_status(self):
        self.read_var(self.index_to_hex(ListVar_v2_1.index('ps_status')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        status = {}
        status['state'] =     ListOpMode_v2_1[(val[3] & 0b0000000000001111)]
        status['open_loop'] = (val[3] & 0b0000000000010000) >> 4
        status['interface'] = (val[3] & 0b0000000001100000) >> 5
        status['active'] =    (val[3] & 0b0000000010000000) >> 7
        status['model'] =     ListPSModels_v2_1[(val[3] & 0b0001111100000000) >> 8]
        status['unlocked'] =  (val[3] & 0b0010000000000000) >> 13
        print(status)
        return status

    def set_ps_name(self,ps_name):
        if type(ps_name) == str:
            for n in range(len(ps_name)):
                self.set_param('PS_Name', n, float(ord(ps_name[n])))
            for i in range(n+1,64):
                self.set_param('PS_Name', i, float(ord(" ")))

    def get_ps_name(self):
        ps_name = ""
        for n in range(64):
            ps_name = ps_name + chr(int(self.get_param('PS_Name', n)))
        return ps_name

    def set_slowref(self,setpoint):
        payload_size   = self.size_to_hex(1+4) #Payload: ID + iSlowRef
        hex_setpoint   = self.float_to_hex(setpoint)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_slowref'))+hex_setpoint
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def set_slowref_fbp(self, iRef1 = 0, iRef2 = 0, iRef3 = 0, iRef4 = 0):
        payload_size = self.size_to_hex(1+4*4) #Payload: ID + 4*iRef
        hex_iRef1    = self.float_to_hex(iRef1)
        hex_iRef2    = self.float_to_hex(iRef2)
        hex_iRef3    = self.float_to_hex(iRef3)
        hex_iRef4    = self.float_to_hex(iRef4)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_slowref_fbp'))+hex_iRef1+hex_iRef2+hex_iRef3+hex_iRef4
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def set_slowref_readback(self,setpoint):
        payload_size   = self.size_to_hex(1+4) #Payload: ID + iSlowRef
        hex_setpoint   = self.float_to_hex(setpoint)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_slowref_readback'))+hex_setpoint
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def set_slowref_fbp_readback(self, iRef1 = 0, iRef2 = 0, iRef3 = 0, iRef4 = 0):
        payload_size = self.size_to_hex(1+4*4) #Payload: ID + 4*iRef
        hex_iRef1    = self.float_to_hex(iRef1)
        hex_iRef2    = self.float_to_hex(iRef2)
        hex_iRef3    = self.float_to_hex(iRef3)
        hex_iRef4    = self.float_to_hex(iRef4)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_slowref_fbp_readback'))+hex_iRef1+hex_iRef2+hex_iRef3+hex_iRef4
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(21)
        if(len(reply_msg) == 6):
            return reply_msg
        else:
            val = struct.unpack('BBHffffB',reply_msg)
            return [val[3],val[4],val[5],val[6]]

    def set_param(self, param_id, n, value):
        payload_size = self.size_to_hex(1+2+2+4) #Payload: ID + param id + [n] + value
        if type(param_id) == str:
            hex_id       = self.double_to_hex(ListParameters.index(param_id))
        if type(param_id) == int:
            hex_id       = self.double_to_hex(param_id)
        hex_n        = self.double_to_hex(n)
        hex_value    = self.float_to_hex(value)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_param'))+hex_id+hex_n+hex_value
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(6)
        if reply_msg[4] == 8:
            print('Invalid parameter')
        return reply_msg

    def get_param(self, param_id, n = 0):
        payload_size = self.size_to_hex(1+2+2) #Payload: ID + param id + [n]
        if type(param_id) == str:
            hex_id       = self.double_to_hex(ListParameters.index(param_id))
        if type(param_id) == int:
            hex_id       = self.double_to_hex(param_id)
        hex_n        = self.double_to_hex(n)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('get_param'))+hex_id+hex_n
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(9)
        if len(reply_msg) == 9:
            val = struct.unpack('BBHfB',reply_msg)
            return val[3]
        else:
            #print('Invalid parameter')
            return float('nan')

    def save_param_eeprom(self, param_id, n = 0):
        payload_size = self.size_to_hex(1+2+2) #Payload: ID + param id + [n] + value
        if type(param_id) == str:
            hex_id       = self.double_to_hex(ListParameters.index(param_id))
        if type(param_id) == int:
            hex_id       = self.double_to_hex(param_id)
        hex_n        = self.double_to_hex(n)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('save_param_eeprom'))+hex_id+hex_n
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(6)
        if reply_msg[4] == 8:
            print('Invalid parameter')
        return reply_msg

    def load_param_eeprom(self, param_id, n = 0):
        payload_size = self.size_to_hex(1+2+2) #Payload: ID + param id + [n]
        if type(param_id) == str:
            hex_id       = self.double_to_hex(ListParameters.index(param_id))
        if type(param_id) == int:
            hex_id       = self.double_to_hex(param_id)
        hex_n        = self.double_to_hex(n)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('load_param_eeprom'))+hex_id+hex_n
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(6)
        if reply_msg[4] == 8:
            print('Invalid parameter')
        return reply_msg

    def save_param_bank(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('save_param_bank'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def load_param_bank(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('load_param_bank'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def set_param_bank(self, param_file):
        fbp_param_list = []
        with open(param_file,newline='') as f:
            reader = csv.reader(f)
            for row in reader:
                fbp_param_list.append(row)

        for param in fbp_param_list:
            if str(param[0]) == 'PS_Name':
                print(str(param[0]) + "[0]: " + str(param[1]))
                print(self.set_ps_name(str(param[1])))
            else:
                for n in range(64):
                    try:
                        print(str(param[0]) + "["+ str(n) + "]: " + str(param[n+1]))
                        print(self.set_param(str(param[0]),n,float(param[n+1])))
                    except:
                        break
        self.save_param_bank()

    def get_param_bank(self):
        timeout_old = self.ser.timeout
        self.ser.timeout = 0.05

        for param in ListParameters:
            for n in range(64):
                if param == 'PS_Name':
                    print('PS_Name: ' + self.get_ps_name())
                    break
                else:
                    p = self.get_param(param,n)
                    if math.isnan(p):
                        break
                    print(param + "[" + str(n) + "]: " + str(p))

        self.ser.timeout = timeout_old

    def set_dsp_coeffs(self, dsp_class, dsp_id, coeffs_list = [0,0,0,0,0,0,0,0,0,0,0,0]):
        coeffs_list_full = self.format_list_size(coeffs_list, NUM_MAX_COEFFS_DSP)
        payload_size = self.size_to_hex(1+2+2+4*NUM_MAX_COEFFS_DSP)
        hex_dsp_class= self.double_to_hex(dsp_class)
        hex_dsp_id   = self.double_to_hex(dsp_id)
        hex_coeffs    = self.float_list_to_hex(coeffs_list_full)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_dsp_coeffs'))+hex_dsp_class+hex_dsp_id+hex_coeffs
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def get_dsp_coeff(self, dsp_class, dsp_id, coeff):
        payload_size = self.size_to_hex(1+2+2+2)
        hex_dsp_class= self.double_to_hex(dsp_class)
        hex_dsp_id   = self.double_to_hex(dsp_id)
        hex_coeff    = self.double_to_hex(coeff)
        print((ListFunc_v2_1.index('get_dsp_coeff')))
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('get_dsp_coeff'))+hex_dsp_class+hex_dsp_id+hex_coeff
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(9)
        print('reply_msg:')
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def save_dsp_coeffs_eeprom(self, dsp_class, dsp_id):
        payload_size = self.size_to_hex(1+2+2)
        hex_dsp_class= self.double_to_hex(dsp_class)
        hex_dsp_id   = self.double_to_hex(dsp_id)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('save_dsp_coeffs_eeprom'))+hex_dsp_class+hex_dsp_id
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def load_dsp_coeffs_eeprom(self, dsp_class, dsp_id):
        payload_size = self.size_to_hex(1+2+2)
        hex_dsp_class= self.double_to_hex(dsp_class)
        hex_dsp_id   = self.double_to_hex(dsp_id)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('load_dsp_coeffs_eeprom'))+hex_dsp_class+hex_dsp_id
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def save_dsp_modules_eeprom(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('save_dsp_modules_eeprom'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def load_dsp_modules_eeprom(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('load_dsp_modules_eeprom'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def reset_udc(self):
        payload_size   = self.size_to_hex(1) #Payload: ID
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('reset_udc'))
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))

    def run_bsmp_func(self,id_func,print_msg = 0):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(id_func)
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        reply_msg = self.ser.read(6)
        if print_msg:
            print(reply_msg)
        return reply_msg

    def run_bsmp_func_all_ps(self,p_func,add_list,arg = None,delay = 0.5):
        old_add = self.GetSlaveAdd()
        for add in add_list:
            self.SetSlaveAdd(add)
            if arg == None:
                p_func()
            else:
                p_func(arg)
            time.sleep(delay)
        self.SetSlaveAdd(old_add)

    def sync_pulse(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('sync_pulse'))
        send_msg     = self.checksum(self.BCastAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def select_op_mode(self,op_mode):
        payload_size = self.size_to_hex(1+2) #Payload: ID + enable
        hex_op_mode  = self.double_to_hex(ListOpMode_v2_1.index(op_mode))
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('select_op_mode'))+hex_op_mode
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def set_serial_termination(self,term_enable):
        payload_size = self.size_to_hex(1+2) #Payload: ID + enable
        hex_enable  = self.double_to_hex(term_enable)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc_v2_1.index('set_serial_termination'))+hex_enable
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def cfg_siggen(self,sig_type,num_cycles,freq,amplitude,offset,aux0,aux1,aux2,aux3):
        payload_size   = self.size_to_hex(1+2+2+4+4+4+4*4)
        hex_sig_type   = self.double_to_hex(sig_type)
        hex_num_cycles = self.double_to_hex(num_cycles)
        hex_freq       = self.float_to_hex(freq)
        hex_amplitude  = self.float_to_hex(amplitude)
        hex_offset     = self.float_to_hex(offset)
        hex_aux0       = self.float_to_hex(aux0)
        hex_aux1       = self.float_to_hex(aux1)
        hex_aux2       = self.float_to_hex(aux2)
        hex_aux3       = self.float_to_hex(aux3)
        send_packet    = self.ComFunction + payload_size + self.index_to_hex(ListFunc_v2_1.index('cfg_siggen')) + hex_sig_type + hex_num_cycles + hex_freq + hex_amplitude + hex_offset + hex_aux0 + hex_aux1 + hex_aux2 + hex_aux3
        send_msg      = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def set_siggen(self,freq,amplitude,offset):
        payload_size   = self.size_to_hex(1+4+4+4)
        hex_freq       = self.float_to_hex(freq)
        hex_amplitude  = self.float_to_hex(amplitude)
        hex_offset     = self.float_to_hex(offset)
        send_packet    = self.ComFunction + payload_size + self.index_to_hex(ListFunc_v2_1.index('set_siggen')) + hex_freq + hex_amplitude + hex_offset
        send_msg      = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def enable_siggen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size + self.index_to_hex(ListFunc_v2_1.index('enable_siggen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def disable_siggen(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size + self.index_to_hex(ListFunc_v2_1.index('disable_siggen'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Leitura de Valores das Variáveis BSMP
    O retorno do método são os valores double/float da respectiva variavel
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def read_bsmp_variable(self,id_var,type_var,print_msg = 0):
        self.read_var(self.index_to_hex(id_var))
        reply_msg = self.ser.read(typeSize[type_var])
        if print_msg:
            print(reply_msg)
        val = struct.unpack(typeFormat[type_var],reply_msg)
        return val[3]

    def read_bsmp_variable_gen(self,id_var,size_bytes,print_msg = 0):
        self.read_var(self.index_to_hex(id_var))
        reply_msg = self.ser.read(size_bytes+5)
        if print_msg:
            print(reply_msg)
        return reply_msg

    def read_udc_arm_version(self):
        self.read_var(self.index_to_hex(3))
        reply_msg = self.ser.read(133)
        val = struct.unpack('16s',reply_msg[4:20])
        return val[0].decode('utf-8')

    def read_udc_c28_version(self):
        self.read_var(self.index_to_hex(3))
        reply_msg = self.ser.read(133)
        val = struct.unpack('16s',reply_msg[20:36])
        return val[0].decode('utf-8')

    def Read_iLoad1(self):
        self.read_var(self.index_to_hex(ListVar.index('iLoad1')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iLoad2(self):
        self.read_var(self.index_to_hex(ListVar.index('iLoad2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('iMod4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vLoad(self):
        self.read_var(self.index_to_hex(ListVar.index('vLoad')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod1')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod2')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod3')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod4')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod1')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod2')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod3')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod4')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp1(self):
        self.read_var(self.index_to_hex(ListVar.index('temp1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp2(self):
        self.read_var(self.index_to_hex(ListVar.index('temp2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp3(self):
        self.read_var(self.index_to_hex(ListVar.index('temp3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_temp4(self):
        self.read_var(self.index_to_hex(ListVar.index('temp4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_ps_OnOff(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OnOff')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_OpMode(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OpMode')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_Remote(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_Remote')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_OpenLoop(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_OpenLoop')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_ps_SoftInterlocks(self):
        op_bin = 1
        ActiveSoftInterlocks = []

        SoftInterlocksList = ['N/A', 'Sobre-tensao na carga 1', 'N/A',\
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 2', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 3', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 4', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        self.read_var(self.index_to_hex(ListVar.index('ps_SoftInterlocks')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHIB',reply_msg)

        print('Soft Interlocks ativos:')
        for i in range(len('{0:b}'.format(val[3]))):
            if (val[3] & (op_bin << i)) == 2**i:
                ActiveSoftInterlocks.append(SoftInterlocksList[i])
                print(SoftInterlocksList[i])
        print('---------------------------------------------------------------')
        return val[3]

    def Read_ps_HardInterlocks(self):
        op_bin = 1
        ActiveHardInterlocks = []

        HardInterlocksList = ['Sobre-corrente na carga 1', 'N/A',                  \
                             'Sobre-tensao no DC-Link do modulo 1',                \
                             'Sub-tensao no DC-Link do modulo 1',                  \
                             'Falha no rele de entrada do DC-Link do modulo 1',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 1', \
                             'Falha nos drivers do modulo 1',                      \
                             'Sobre-temperatura no modulo 1',                      \
                             'Sobre-corrente na carga 2', 'N/A',                   \
                             'Sobre-tensao no DC-Link do modulo 2',                \
                             'Sub-tensao no DC-Link do modulo 2',                  \
                             'Falha no rele de entrada do DC-Link do modulo 2',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 2', \
                             'Falha nos drivers do modulo 2',                      \
                             'Sobre-temperatura no modulo 2',                      \
                             'Sobre-corrente na carga 3', 'N\A',                   \
                             'Sobre-tensao no DC-Link do modulo 3',                \
                             'Sub-tensao no DC-Link do modulo 3',                  \
                             'Falha no rele de entrada no DC-Link do modulo 3',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 3', \
                             'Falha nos drivers do modulo 3',                      \
                             'Sobre-temperatura no modulo 3',                      \
                             'Sobre-corrente na carga 4', 'N/A',                   \
                             'Sobre-tensao no DC-Link do modulo 4',                \
                             'Sub-tensao no DC-Link do modulo 4',                  \
                             'Falha no rele de entrada do DC-Link do modulo 4',    \
                             'Falha no fusivel de entrada do DC-Link do modulo 4', \
                             'Falha nos drivers do modulo 4',                      \
                             'Sobre-temperatura no modulo 4']

        self.read_var(self.index_to_hex(ListVar.index('ps_HardInterlocks')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHIB',reply_msg)

        print('Hard Interlocks ativos:')
        for i in range(len('{0:b}'.format(val[3]))):
            if (val[3] & (op_bin << i)) == 2**i:
                ActiveHardInterlocks.append(HardInterlocksList[i])
                print(HardInterlocksList[i])
        print('---------------------------------------------------------------')
        return val[3]

    def Read_iRef(self):
        self.read_var(self.index_to_hex(ListVar.index('iRef')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_wfmRef_Gain(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_Gain')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_wfmRef_Offset(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_Offset')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Enable(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Enable')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_Type(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Type')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_Ncycles(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Ncycles')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_sigGen_PhaseStart(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_PhaseStart')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_PhaseEnd(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_PhaseEnd')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Freq(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Freq')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Amplitude(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Amplitude')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Offset(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Offset')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_sigGen_Aux(self):
        self.read_var(self.index_to_hex(ListVar.index('sigGen_Aux')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_dp_ID(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_ID')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_dp_Class(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_Class')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_dp_Coeffs(self):
        self.read_var(self.index_to_hex(ListVar.index('dp_Coeffs')))
        reply_msg = self.ser.read(69)
        val = struct.unpack('BBHffffffffffffffffB',reply_msg)
        return [val[3],val[4],val[5],val[6],val[7],val[8],val[9],val[10],val[11],val[12],val[13],val[14],val[15],val[16],val[17],val[18]]

    def Read_ps_Model(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_Model')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val

    def read_ps_model(self):
        reply_msg = self.Read_ps_Model()
        return ListPSModels[reply_msg[3]]

    def Read_wfmRef_PtrBufferStart(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_PtrBufferStart')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHIB',reply_msg)
        return val[3]

    def Read_wfmRef_PtrBufferEnd(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_PtrBufferEnd')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHIB',reply_msg)
        return val[3]

    def Read_wfmRef_PtrBufferK(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_PtrBufferK')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHIB',reply_msg)
        return val[3]

    def Read_wfmRef_SyncMode(self):
        self.read_var(self.index_to_hex(ListVar.index('wfmRef_SyncMode')))
        reply_msg = self.ser.read(7)
        val = struct.unpack('BBHHB',reply_msg)
        return val[3]

    def Read_iRef1(self):
        self.read_var(self.index_to_hex(45))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iRef2(self):
        self.read_var(self.index_to_hex(46))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iRef3(self):
        self.read_var(self.index_to_hex(47))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_iRef4(self):
        self.read_var(self.index_to_hex(48))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_counterSetISlowRefx4(self):
        self.read_var(self.index_to_hex(49))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Escrita de Valores das Variáveis BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def Write_sigGen_Freq(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Freq'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Amplitude(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Amplitude'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Offset(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Offset'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_sigGen_Aux(self,float_value):
        hex_float    = self.float_to_hex(float_value)
        send_packet  = self.ComWriteVar+self.WriteFloatSizePayload+self.index_to_hex(ListVar.index('sigGen_Aux'))+hex_float
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_ID(self,double_value):
        hex_double   = self.double_to_hex(double_value)
        send_packet  = self.ComWriteVar+self.WriteDoubleSizePayload+self.index_to_hex(ListVar.index('dp_ID'))+hex_double
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_Class(self,double_value):
        hex_double   = self.double_to_hex(double_value)
        send_packet  = self.ComWriteVar+self.WriteDoubleSizePayload+self.index_to_hex(ListVar.index('dp_Class'))+hex_double
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Write_dp_Coeffs(self,list_float):

        hex_float_list = []
        #list_full = list_float[:]

        #while(len(list_full) < self.DP_MODULE_MAX_COEFF):
        #    list_full.append(0)

        list_full = [0 for i in range(self.DP_MODULE_MAX_COEFF)]
        list_full[:len(list_float)] = list_float[:]

        for float_value in list_full:
            hex_float = self.float_to_hex(float(float_value))
            hex_float_list.append(hex_float)
        str_float_list = ''.join(hex_float_list)
        payload_size = self.size_to_hex(1+4*self.DP_MODULE_MAX_COEFF) #Payload: ID + 16floats
        send_packet  = self.ComWriteVar+payload_size+self.index_to_hex(ListVar.index('dp_Coeffs'))+str_float_list
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                     Métodos de Escrita de Curvas BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    def Send_wfmRef_Curve(self,block_idx,data):
        block_hex = struct.pack('>H',block_idx).decode('ISO-8859-1')
        val   = []
        for k in range(0,len(data)):
           val.append(self.float_to_hex(float(data[k])))
        payload_size  = struct.pack('>H', (len(val)*4)+3).decode('ISO-8859-1')
        curva_hex     = ''.join(val)
        send_packet   = self.ComSendWfmRef+payload_size+self.index_to_hex(ListCurv.index('wfmRef_Curve'))+block_hex+curva_hex
        send_msg      = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Recv_wfmRef_Curve(self,block_idx):
        block_hex    = struct.pack('>H',block_idx).decode('ISO-8859-1')
        payload_size = self.size_to_hex(1+2) #Payload: ID+Block_index
        send_packet  = self.ComRequestCurve+payload_size+self.index_to_hex(ListCurv.index('wfmRef_Curve'))+block_hex
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        recv_msg = self.ser.read(1+1+2+1+2+8192+1) #Address+Command+Size+ID+Block_idx+data+checksum
        val = []
        for k in range(7,len(recv_msg)-1,4):
            val.append(struct.unpack('f',recv_msg[k:k+4]))
        return val

    def Recv_samplesBuffer(self):
        block_hex    = struct.pack('>H',0).decode('ISO-8859-1')
        payload_size = self.size_to_hex(1+2) #Payload: ID+Block_index
        send_packet  = self.ComRequestCurve+payload_size+self.index_to_hex(ListCurv.index('samplesBuffer'))+block_hex
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        recv_msg = self.ser.read(1+1+2+1+2+16384+1) #Address+Command+Size+ID+Block_idx+data+checksum
        val = []
        try:
            for k in range(7,len(recv_msg)-1,4):
                val.extend(struct.unpack('f',recv_msg[k:k+4]))
        except:
            pass
        return val

    def Send_fullwfmRef_Curve(self,block_idx,data):
        block_hex = struct.pack('>H',block_idx).decode('ISO-8859-1')
        val   = []
        for k in range(0,len(data)):
           val.append(self.float_to_hex(float(data[k])))
        payload_size  = struct.pack('>H', (len(val)*4)+3).decode('ISO-8859-1')
        curva_hex     = ''.join(val)
        send_packet   = self.ComSendWfmRef+payload_size+self.index_to_hex(ListCurv.index('fullwfmRef_Curve'))+block_hex+curva_hex
        send_msg      = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(5)

    def Recv_fullwfmRef_Curve(self,block_idx):
        block_hex    = struct.pack('>H',block_idx).decode('ISO-8859-1')
        payload_size = self.size_to_hex(1+2) #Payload: ID+Block_index
        send_packet  = self.ComRequestCurve+payload_size+self.index_to_hex(ListCurv.index('fullwfmRef_Curve'))+block_hex
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        recv_msg = self.ser.read(1+1+2+1+2+16384+1) #Address+Command+Size+ID+Block_idx+data+checksum
        val = []
        for k in range(7,len(recv_msg)-1,4):
            val.append(struct.unpack('f',recv_msg[k:k+4]))
        return val

    def Recv_samplesBuffer_blocks(self,block_idx):
        block_hex    = struct.pack('>H',block_idx).decode('ISO-8859-1')
        payload_size = self.size_to_hex(1+2) #Payload: ID+Block_index
        send_packet  = self.ComRequestCurve+payload_size+self.index_to_hex(ListCurv.index('samplesBuffer_blocks'))+block_hex
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        #t0 = time.time()
        self.ser.write(send_msg.encode('ISO-8859-1'))
        recv_msg = self.ser.read(1+1+2+1+2+1024+1) #Address+Command+Size+ID+Block_idx+data+checksum
        #print(time.time()-t0)
        #print(recv_msg)
        val = []
        for k in range(7,len(recv_msg)-1,4):
            val.extend(struct.unpack('f',recv_msg[k:k+4]))
        return val

    def Recv_samplesBuffer_allblocks(self):
        buff = []
        #self.DisableSamplesBuffer()
        for i in range(0,16):
            #t0 = time.time()
            buff.extend(self.Recv_samplesBuffer_blocks(i))
            #print(time.time()-t0)
        #self.EnableSamplesBuffer()
        return buff


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                            Funções Serial
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def Connect(self,port='COM2',baud=6000000):
        try:
            SerialDRS.ser = serial.Serial(port,baud,timeout=1) #port format should be 'COM'+number
            return True
        except:
            return False

    def Disconnect(self):
        if (self.ser.isOpen()):
            try:
                self.ser.close()
                return True
            except:
                return False

    def SetSlaveAdd(self,address):
        self.SlaveAdd = struct.pack('B',address).decode('ISO-8859-1')

    def GetSlaveAdd(self):
        return struct.unpack('B',self.SlaveAdd.encode())[0]

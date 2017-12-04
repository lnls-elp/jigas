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
            'SetRSAddress','EnableSamplesBuffer','DisableSamplesBuffer','SelectHRADCBoard','SelectTestSource',
            'ResetHRADCBoards','Config_nHRADC','ReadHRADC_UFM','WriteHRADC_UFM','EraseHRADC_UFM','ReadHRADC_BoardData']
ListTestFunc = ['UdcIoExpanderTest', 'UdcLedTest', 'UdcBuzzerTest', 'UdcEepromTest', 'UdcFlashTest', 'UdcRamTest',
                'UdcRtcTest', 'UdcSensorTempTest', 'UdcIsoPlaneTest', 'UdcAdcTest', 'UdcUartTest', 'UdcLoopBackTest',
                'UdcComTest', 'UdcI2cIsoTest']
ListHRADCInputType = ['Vin_bipolar','Vin_unipolar_p','Vin_unipolar_n','Iin_bipolar','Iin_unipolar_p',
                      'Iin_unipolar_n','Vref_bipolar_p','Vref_bipolar_n','GND','Vref_unipolar_p',
                      'Vref_unipolar_n','GND_unipolar','Temp','Reserved0','Reserved1','Reserved2']

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
        self.ser.write(send_msg.encode('ISO-8859-1'))

    def is_open(self):
        return self.ser.isOpen()

    def read_HardInterlock(self, int_interlock):
        HardInterlockList = ['Sobre-corrente na carga 1', 'N/A',                   \
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
        op_bin = 1
        ActiveHardInterlocks = []

        print('Hard Interlocks ativos:')

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveHardInterlocks.append(HardInterlockList[i])
                print(HardInterlockList[i])
        print('-------------------------------------------------------------------')

        return ActiveHardInterlocks

    def read_SoftInterlock(self, int_interlock):
        SoftInterlockList = ['N/A', 'Sobre-tensao na carga 1', 'N/A', \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 2', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 3', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A',\
                             'Sobre-tensao na carga 4', 'N/A',        \
                             'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A']

        op_bin = 1
        ActiveSoftInterlocks = []

        print('Soft Interlocks ativos:')

        for i in range(len('{0:b}'.format(int_interlock))):
            if (int_interlock & (op_bin << i)) == 2**i:
                ActiveSoftInterlocks.append(SoftInterlockList[i])
                print(SoftInterlockList[i])
        print('-------------------------------------------------------------------')

        return ActiveSoftInterlocks

    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Chamada de Entidades Funções BSMP
            O retorno do método são os bytes de retorno da mensagem
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def TurnOn(self,ps_modules):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_modules
        hex_modules  = self.double_to_hex(ps_modules)
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('TurnOn'))+hex_modules
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

    def ReadHRADC_BoardData(self,hradcID):
        payload_size   = self.size_to_hex(1+2) #Payload: ID + hradcID
        hex_hradcID    = self.double_to_hex(hradcID)
        send_packet    = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('ReadHRADC_BoardData'))+hex_hradcID
        send_msg       = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

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
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(23)+hex_iRef1+hex_iRef2+hex_iRef3+hex_iRef4
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Leitura de Valores das Variáveis BSMP
    O retorno do método são os valores double/float da respectiva variavel
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

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
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vDCMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('vDCMod4')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod1(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod1')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod2(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod2')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod3(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod3')))
        reply_msg = self.ser.read(9)
        val = struct.unpack('BBHfB',reply_msg)
        return val[3]

    def Read_vOutMod4(self):
        self.read_var(self.index_to_hex(ListVar.index('vOutMod4')))
        reply_msg = self.ser.read(9)
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
        self.read_var(self.index_to_hex(ListVar.index('ps_SoftInterlocks')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHIB',reply_msg)
        return val[3]

    def Read_ps_HardInterlocks(self):
        self.read_var(self.index_to_hex(ListVar.index('ps_HardInterlocks')))
        reply_msg = self.ser.read(9)
        print(reply_msg)
        val = struct.unpack('BBHIB',reply_msg)
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

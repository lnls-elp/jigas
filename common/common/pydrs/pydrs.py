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

ListCurv = ['wfmRef_Curve','sigGen_SweepAmp','samplesBuffer','fullwfmRef_Curve','wfmRef_Blocks','samplesBuffer_blocks']

ListHRADCInputType = ['Vin_bipolar','Vin_unipolar_p','Vin_unipolar_n','Iin_bipolar','Iin_unipolar_p',
                      'Iin_unipolar_n','Vref_bipolar_p','Vref_bipolar_n','GND','Vref_unipolar_p',
                      'Vref_unipolar_n','GND_unipolar','Temp','Reserved0','Reserved1','Reserved2']

ListVar = ['ps_status','ps_setpoint','ps_reference','wfmref_selected',
                'wfmref_sync_mode','wfmref_gain','wfmref_offset',
                'p_wfmref_start','p_wfmref_end','p_wfmref_idx']

ListFunc = ['turn_on','turn_off','open_loop','closed_loop','cfg_op_mode',
                 'cfg_ps_model','reset_interlocks','remote_interface',''
                 'set_serial_address','set_serial_termination','unlock_udc',
                 'lock_udc','cfg_buf_samples','enable_buf_samples',
                 'disable_buf_samples','sync_pulse','set_slowref',
                 'set_slowref_fbp']

typeFormat = {'uint16_t': 'BBHHB', 'uint32_t': 'BBHIB', 'float': 'BBHfB'}
typeSize   = {'uint16_t': 7, 'uint32_t': 9, 'float': 9}
operation_mode = {'SlowRef': 3, 'SlowRefSync': 4, 'FastRef': 5, 'RmpWfm': 6, 'MigWfm': 7, 'Cycle': 8}

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

    def turn_on(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('turn_on'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def turn_off(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('turn_off'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def open_loop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('open_loop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def closed_loop(self):
        payload_size = self.size_to_hex(1) #Payload: ID
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('closed_loop'))
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)

    def cfg_op_mode(self,mode):
        payload_size = self.size_to_hex(1+2) #Payload: ID + ps_opmode
        hex_opmode   = self.double_to_hex(operation_mode[mode])
        send_packet  = self.ComFunction+payload_size+self.index_to_hex(ListFunc.index('cfg_op_mode'))+hex_opmode
        send_msg     = self.checksum(self.SlaveAdd+send_packet)
        self.ser.write(send_msg.encode('ISO-8859-1'))
        return self.ser.read(6)


    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
    ======================================================================
                Métodos de Leitura de Valores das Variáveis BSMP
    O retorno do método são os valores double/float da respectiva variavel
    ======================================================================
    '''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''

    def read_bsmp_variable(self,id_var,type_var,print_msg):
        self.read_var(self.index_to_hex(id_var))
        reply_msg = self.ser.read(typeSize[type_var])
        if print_msg:
            print(reply_msg)
        val = struct.unpack(typeFormat[type_var],reply_msg)
        return val[3]


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

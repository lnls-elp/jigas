from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.hradcdata import HRADC, HRADCLog
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
from common.keysight3458A import Keysight3458A_GPIB
from common.krohnhite523 import KrohnHite523_GPIB

import serial
import random
import time
import struct
import numpy as np

class HRADCTest(QThread):

    test_complete       = pyqtSignal(list)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    device = {'HRADC':1, 'DM':2}
    bytesFormat = {'Uint16': 'H', 'Uint32': 'L', 'Uint64': 'Q', 'float': 'f'}
    ufmOffset = {'serial': 0, 'calibdate': 4, 'variant': 9, 'rburden': 10}
    hradcVariant = {'HRADC-FBP': 0, 'HRADC-FAX': 1}
    hradcInputTypes = ['GND', 'Vref_bipolar_p', 'Vref_bipolar_n', 'Temp',
                       'Vin_bipolar', 'Iin_bipolar']

    def __init__(self):
        QThread.__init__(self)
        self._comport = 'COM2'
        self._baudrate = 6000000
        ser = str(input('Leia S/N: '))
        ser = int(ser[2:])
        self._boardsinfo = [{'serial' : ser,
                             'variant' : 'HRADC-FAX',
                             'pre_tests' : 'Firmware gravado com sucesso',
                             'slot' : 1}]
        self._nHRADC = None
        self._led = None

        self.drs = SerialDRS()
        self.source = KrohnHite523_GPIB()
        self.dmm = Keysight3458A_GPIB()

        self.refVal = {'GND': 0,
                       'Vref_bipolar_p': 5,
                       'Vref_bipolar_n': -5,
                       'Temp': -0.35,
                       'Vin_bipolar': 10,
                       'Iin_bipolar': 0.05
                       }

        self.refTol = {'GND': 0.02,
                       'Vref_bipolar_p': 0.02,
                       'Vref_bipolar_n': 0.02,
                       'Temp': 0.1,
                       'Vin_bipolar': 0.02,
                       'Iin_bipolar': 0.0001}

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value

    @property
    def baudrate(self):
        return self._baudrate

    @baudrate.setter
    def baudrate(self, value):
        self._baudrate = value

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value

    @property
    def firmware_error(self):
        return self._firmware_error

    @firmware_error.setter
    def firmware_error(self, value):
        self._firmware_error = value

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            self.dmm.Connect('GPIB0::22::INSTR')
            self.source.Connect('GPIB0::25::INSTR')

            self.source.DisableOutput()
            self.source.Reset()
            self.source.LOFloatChassis('F')
            self.source.OutputTermination(0)
            self.source.SetVoltageLimit(2)
            self.source.SetOutput(0,'V')

            self.dmm.InitDefault()
            self.dmm.SetMeasurementType('DCV',10)
            self.dmm.SetMultipointMeas(3)

            return self.drs.Connect(self._comport, self._baudrate)

    def test_communication(self,slot):

        try:
            test_package = self.drs.Read_ps_Model()
            print(test_package)
            if (test_package[0] == 0) and (test_package[1] == 17) and (test_package[2] == 512) and (test_package[3] == 10) and (test_package[4] == 227):
                print('Comunicando com HRADC...')
                self.drs.Config_nHRADC(slot)
                time.sleep(1)
                print('Resetando HRADC...')
                self.drs.ResetHRADCBoards(1)
                time.sleep(1)
                self.drs.ResetHRADCBoards(0)
                time.sleep(1)
                print('Configurando HRADC...\n')
                self.drs.ConfigHRADC(slot-1,100000,'GND',0,0)
                time.sleep(0.1)
                print('Habilita SamplesBuffer...\n')
                self.drs.EnableSamplesBuffer()
                time.sleep(0.1)
                print('Habilita Sampling...\n')
                self.drs.EnableHRADCSampling()
                time.sleep(1)
                print('Desabilita SamplesBuffer...\n')
                self.drs.DisableSamplesBuffer()
                time.sleep(0.1)
                print('Desabilita Sampling...\n')
                self.drs.DisableHRADCSampling()
                time.sleep(0.1)
                print('Le SamplesBuffer...\n')
                buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                print(buff)
                hradcMean = buff.mean()
                print(hradcMean)
                if abs(hradcMean) < self.refTol['GND']:
                    print('TRUE')
                    return True

                print('FALSE')
                return False

        except:
            print('EXCEPT')
            self.drs.DisableHRADCSampling()
            return False

    def _test_sequence(self):

        print('Valendo!\n')

        print(self._boardsinfo)
        self.nHRADC = max([board['slot'] for board in self._boardsinfo])
        print('Configurando nHRADC...\n')
        self.drs.Config_nHRADC(self.nHRADC)
        time.sleep(1)
        print('Resetando HRADC...\n')
        self.drs.ResetHRADCBoards(1)
        time.sleep(1)
        self.drs.ResetHRADCBoards(0)
        log_res = []

        print('Començando a ler boardsinfo...\n')

        for board in self._boardsinfo:

            print('\n**********************************')
            print('**************   Slot ' + str(board['slot']) + '   ********')
            print('**********************************\n\n')
            print(board)

            hradc = HRADC()
            ufmdata_16 = []
            emptyBuff = np.array([])

            hradc.serial_number = board['serial']
            hradc.variant = board['variant']
            hradc.burden_amplifier = "INA141"

            if hradc.variant == 'HRADC-FBP':
                hradc.burden_res = 20.0
                hradc.cut_frequency = 48228.7
                hradc.filter_order = 1

            print('\nEnviando ao servidor dados desta placa...\n')
            res = self._send_to_server(hradc)

            if res:
                print(res)
                print('\n')

                log_hradc = HRADCLog()
                log_hradc.serial_number_hradc = board['serial']
                log_hradc.device = self.device['HRADC']
                log_hradc.test_result = "Aprovado"
                log_hradc.details = board['pre_tests']

                log_dm = HRADCLog()
                log_dm.serial_number_hradc = board['serial']
                log_dm.device = self.device['DM']
                log_dm.test_result = "Aprovado"

                if board['slot'] > 0:

                    print('Colocando em UFM mode a placa bem sucedida do slot ' + str(board['slot'])+ '\n')

                    board['slot'] = board['slot'] - 1
                    self.drs.ConfigHRADCOpMode(board['slot'],1)
                    time.sleep(0.5)

                    print('Enviando serial number...')
                    # Send serial number
                    ufmdata_16 = self._convertToUint16List(board['serial'],'Uint64')
                    for i in range(len(ufmdata_16)):
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['serial'],ufmdata_16[i])
                        time.sleep(0.1)

                    print('Enviando variante...')
                    # Send variant
                    ufmdata_16 = self._convertToUint16List(self.hradcVariant[board['variant']],'Uint16')
                    for i in range(len(ufmdata_16)):
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['variant'],ufmdata_16[i])
                        time.sleep(0.1)

                    print('Enviando rburden...')
                    # Send Rburden
                    ufmdata_16 = self._convertToUint16List(hradc.burden_res,'float')
                    for i in range(len(ufmdata_16)):
                        self.drs.WriteHRADC_UFM(board['slot'],i+self.ufmOffset['rburden'],ufmdata_16[i])
                        time.sleep(0.1)

                    '''
                    print('Lendo byte')
                    time.sleep(0.5)
                    self.drs.ReadHRADC_UFM(board['slot'],0)
                    '''

                    self.drs.ConfigHRADCOpMode(board['slot'],0)
                    time.sleep(0.5)
                    self._configBoardsToTest(board,'GND')
                    time.sleep(0.5)
                    self.drs.SelectHRADCBoard(board['slot'])
                    time.sleep(0.1)

                    ###################
                    #### TESTE GND ####
                    ###################

                    self.drs.ConfigHRADC(board['slot'],100000,'GND',0,0)
                    time.sleep(0.1)
                    self.drs.SelectTestSource('GND')
                    time.sleep(0.1)
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.gnd = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.gnd = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)


                    print('\n- GND -')
                    print('HRADC: ' + str(log_hradc.gnd) + ' V')
                    print('DMM: ' + str(log_dm.gnd) + ' V\n')

                    if abs(log_hradc.gnd - self.refVal['GND']) > self.refTol['GND']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC GND Reprovado')

                    if abs(log_dm.gnd - self.refVal['GND']) > self.refTol['GND']:
                        log_dm.test_result = "Reprovado"
                        print('DM GND Reprovado')

                    #############################
                    #### TESTE Vref_bipolar_p ###
                    #############################

                    self.drs.ConfigHRADC(board['slot'],100000,'Vref_bipolar_p',0,0)
                    time.sleep(0.1)
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.vref_p = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.vref_p = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)

                    print('- Vref_bipolar_p -')
                    print('HRADC: ' + str(log_hradc.vref_p) + ' V')
                    print('DMM: ' + str(log_dm.vref_p) + ' V\n')

                    if abs(log_hradc.vref_p - self.refVal['Vref_bipolar_p']) > self.refTol['Vref_bipolar_p']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Vref+ Reprovado')

                    if abs(log_dm.vref_p - self.refVal['Vref_bipolar_p']) > self.refTol['Vref_bipolar_p']:
                        log_dm.test_result = "Reprovado"
                        print('DM Vref+ Reprovado')

                    #############################
                    #### TESTE Vref_bipolar_n ###
                    #############################

                    self.drs.ConfigHRADC(board['slot'],100000,'Vref_bipolar_n',0,0)
                    time.sleep(0.1)
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.vref_n = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.vref_n = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)

                    print('- Vref_bipolar_n -')
                    print('HRADC: ' + str(log_hradc.vref_n) + ' V')
                    print('DMM: ' + str(log_dm.vref_n) + ' V\n')

                    if abs(log_hradc.vref_n - self.refVal['Vref_bipolar_n']) > self.refTol['Vref_bipolar_n']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Vref- Reprovado')

                    if abs(log_dm.vref_n - self.refVal['Vref_bipolar_n']) > self.refTol['Vref_bipolar_n']:
                        log_dm.test_result = "Reprovado"
                        print('DM Vref- Reprovado')

                    ####################
                    #### TESTE Temp ####
                    ####################

                    self.drs.ConfigHRADC(board['slot'],100000,'Temp',0,0)
                    time.sleep(0.1)
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.temperature = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.temperature = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)

                    print('- Temp -')
                    print('HRADC: ' + str(log_hradc.temperature) + ' V')
                    print('DMM: ' + str(log_dm.temperature) + ' V\n')

                    if abs(log_hradc.temperature - self.refVal['Temp']) > self.refTol['Temp']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Temp Reprovado')

                    if abs(log_dm.temperature - self.refVal['Temp']) > self.refTol['Temp']:
                        log_dm.test_result = "Reprovado"
                        print('DM Temp Reprovado')

                    #############################
                    #### TESTE Vin_bipolar_p ####
                    #############################

                    self.drs.ConfigHRADC(board['slot'],100000,'Vin_bipolar',0,0)
                    time.sleep(0.1)
                    self.drs.SelectTestSource('Vin_bipolar')
                    time.sleep(0.1)
                    self.source.SetOutput(10,'V')
                    self.source.EnableOutput()
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.vin_p = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.vin_p = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)

                    print('- Vin_bipolar_p -')
                    print('HRADC: ' + str(log_hradc.vin_p) + ' V')
                    print('DMM: ' + str(log_dm.vin_p) + ' V\n')

                    if abs(log_hradc.vin_p - self.refVal['Vin_bipolar']) > self.refTol['Vin_bipolar']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Vin+ Reprovado')

                    if abs(log_dm.vin_p - self.refVal['Vin_bipolar']) > self.refTol['Vin_bipolar']:
                        log_dm.test_result = "Reprovado"
                        print('HRADC Vin+ Reprovado')

                    #############################
                    #### TESTE Vin_bipolar_n ####
                    #############################

                    self.source.SetOutput(-10,'V')
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.vin_n = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.vin_n = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)
                    self.source.DisableOutput()

                    print('- Vin_bipolar_n -')
                    print('HRADC: ' + str(log_hradc.vin_n) + ' V')
                    print('DMM: ' + str(log_dm.vin_n) + ' V\n')


                    if abs(log_hradc.vin_n + self.refVal['Vin_bipolar']) > self.refTol['Vin_bipolar']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Vin- Reprovado')

                    if abs(log_dm.vin_n + self.refVal['Vin_bipolar']) > self.refTol['Vin_bipolar']:
                        log_dm.test_result = "Reprovado"
                        print('DM Vin- Reprovado')

                    #############################
                    #### TESTE Iin_bipolar_p ####
                    #############################

                    self.drs.ConfigHRADC(board['slot'],100000,'Iin_bipolar',0,0)
                    time.sleep(0.1)
                    self.drs.SelectTestSource('Iin_bipolar')
                    time.sleep(0.1)
                    self.dmm.SetMeasurementType('DCI',0.05)
                    self.source.SetOutput(0.05,'I')
                    self.source.EnableOutput()
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.iin_p = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.iin_p = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)

                    print('- Iin_bipolar_p -')
                    print('HRADC: ' + str(log_hradc.iin_p) + ' A')
                    print('DMM: ' + str(log_dm.iin_p) + ' A\n')

                    if board['variant'] == 'HRADC-FBP' and abs(log_hradc.iin_p - self.refVal['Iin_bipolar']) > self.refTol['Iin_bipolar']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Iin+ Reprovado')

                    if board['variant'] == 'HRADC-FBP' and abs(log_dm.iin_p - self.refVal['Iin_bipolar']) > self.refTol['Iin_bipolar']:
                        log_dm.test_result = "Reprovado"
                        print('DM Iin+ Reprovado')

                    #############################
                    #### TESTE Iin_bipolar_n ####
                    #############################

                    self.source.SetOutput(-0.05,'I')
                    self.drs.EnableSamplesBuffer()
                    time.sleep(1)
                    self.drs.EnableHRADCSampling()
                    time.sleep(1)
                    self.drs.DisableSamplesBuffer()
                    time.sleep(0.5)

                    buff = np.array(self.drs.Recv_samplesBuffer_blocks(0))
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_hradc.iin_n = buff.mean()

                    buff = np.array(self.dmm.ReadMeasurementPoints())
                    if np.array_equal(buff,emptyBuff):
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        print('************** FALHA SAMPLES BUFFER **************')
                        return
                    log_dm.iin_n = buff.mean()

                    self.drs.DisableHRADCSampling()
                    time.sleep(0.1)
                    self.source.DisableOutput()

                    print('- Iin_bipolar_n -')
                    print('HRADC: ' + str(log_hradc.iin_n) + ' A')
                    print('DMM: ' + str(log_dm.iin_n) + ' A\n')

                    if board['variant'] == 'HRADC-FBP' and abs(log_hradc.iin_n + self.refVal['Iin_bipolar']) > self.refTol['Iin_bipolar']:
                        log_hradc.test_result = "Reprovado"
                        print('HRADC Iin- Reprovado')

                    if board['variant'] == 'HRADC-FBP' and abs(log_dm.iin_n + self.refVal['Iin_bipolar']) > self.refTol['Iin_bipolar']:
                        log_dm.test_result = "Reprovado"
                        print('DM Iin- Reprovado')


                    print('Salvando log e enviando ao servidor...')
                    log_hradc.details = board['pre_tests']


                    #log_hradc.test_result = "Aprovado"
                    #log_dm.test_result = "Aprovado"

                    log_hradc_serverstatus = self._send_to_server(log_hradc)
                    log_dm_serverstatus = self._send_to_server(log_dm)

                    log_res.append(log_hradc.test_result)

                else:
                    print('Salvando log de placa reprovada enviando ao servidor...')
                    log_hradc.test_result = "Reprovado"
                    log_hradc.details = board['pre_tests']

                    log_hradc_serverstatus = self._send_to_server(log_hradc)

            else:
                print('Falha de comunicacao com servidor!')

                # TODO: incluir falha de comunicacao com servidor no sinal log_res
                #log_res.append('')


        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo HRADCLog

        print('Enviando sinal ao app')

        for i in range(4 - len(log_res)):
            log_res.append(None)
        print('log_res:' + str(log_res))
        self.test_complete.emit(log_res)


    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        print('client_data:\n')
        print(client_data)
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        server_status = self._parse_response(client_response)
        return server_status

    def _parse_response(self, response):
        res_key = 'StatusCode'
        err_key = 'error'

        if res_key in response.keys() and err_key not in response.keys():
            return True
        else:
            return False

    def _convertToUint16List(self, val, format):

        val_16 = []
        val_b = struct.pack(self.bytesFormat[format],val)
        print(val_b)
        for i in range(0,len(val_b),2):
            val_16.append(struct.unpack('H',val_b[i:i+2])[0])
        print(val_16)
        return val_16

    def _configBoardsToTest(self,board,inputType):
        for slot in range(self.nHRADC):
            if slot == board['slot']:
                self.drs.ConfigHRADC(slot,100000,inputType,0,0)
            else:
                self.drs.ConfigHRADC(slot,100000,'GND',0,0)

    def run(self):
        self._test_sequence()
        #pass

if __name__ == '__main__':
    hradc = HRADCTest()
    hradc.open_serial_port()
    hradc._test_sequence()

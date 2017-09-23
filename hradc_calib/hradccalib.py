from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.hradcdata import HRADC, HRADCLogCalib
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
from common.keysight3458A import Keysight3458A_GPIB
from common.krohnhite523 import KrohnHite523_GPIB
from threading import Timer

import serial
import random
import time
import struct

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as anim

class HRADCCalib(QThread):

    calib_complete      = pyqtSignal(bool)
    update_gui          = pyqtSignal(str)
    connection_lost     = pyqtSignal()

    device = {'HRADC':1, 'DM':2}
    bytesFormat = {'Uint16': 'H', 'Uint32': 'L', 'Uint64': 'Q', 'float': 'f'}
    ufmOffset = {'serial': 0, 'calibdate': 4, 'variant': 9, 'rburden': 10,
                 'calibtemp': 12, 'vin_gain': 14, 'vin_offset': 16,
                 'iin_gain': 18, 'iin_offset': 20, 'vref_p': 22, 'vref_n': 24,
                 'gnd': 26}
    hradcVariant = {'HRADC-FBP': 0, 'HRADC-FAX': 1}
    hradcInputTypes = ['GND', 'Vref_bipolar_p', 'Vref_bipolar_n', 'Temp',
                       'Vin_bipolar', 'Iin_bipolar']

    # DMM param
    nplc = 10
    dmmSampleCount = 4

    # DC Source param
    settlingTime = 2

    vin_lsb = 20/pow(2,18)
    vin_step = vin_lsb/5

    iin_lsb = 0.1/pow(2,18)
    iin_step = iin_lsb/4

    def __init__(self):
        QThread.__init__(self)

        self._comport = None
        self._baudrate = None

        self._serial_mod0 = None
        self._serial_mod1 = None
        self._serial_mod2 = None
        self._serial_mod3 = None
        self._serial_list = []

        self._nHRADC = None

        self._led = None

        self.drs = SerialDRS()
        self.source = KrohnHite523_GPIB()
        self.dmm = Keysight3458A_GPIB()

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
    def serial_list(self):
        return self._serial_list

    @serial_list.setter
    def serial_list(self, value_list):
        self._serial_list = value_list

    @property
    def serial_mod0(self):
        return self._serial_mod0

    @serial_mod0.setter
    def serial_mod0(self, value):
        self._serial_mod0 = value

    @property
    def serial_mod1(self):
        return self._serial_mod1

    @serial_mod1.setter
    def serial_mod1(self, value):
        self._serial_mod1 = value

    @property
    def serial_mod2(self):
        return self._serial_mod2

    @serial_mod2.setter
    def serial_mod2(self, value):
        self._serial_mod2 = value

    @property
    def serial_mod3(self):
        return self._serial_mod3

    @serial_mod3.setter
    def serial_mod3(self, value):
        self._serial_mod3 = value

    @property
    def nHRADC(self):
        return self._nHRADC

    @nHRADC.setter
    def nHRADC(self, value):
        self._nHRADC = value

    def _timeout(self):
        print('\nFim do warm-up\n')

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            self.dmm.Connect('GPIB0::22::INSTR')
            self.source.Connect('GPIB0::25::INSTR')

            self.source.DisableOutput()
            #self.source.Reset()
            self.source.LOFloatChassis('F')
            self.source.OutputTermination(0)
            self.source.SetVoltageLimit(2)
            self.source.SetOutput(0,'V')

            self.dmm.InitDefault()
            self.dmm.SetMeasurementType('DCV',10)
            self.dmm.SetMultipointMeas(self.dmmSampleCount)

            return self.drs.Connect(self._comport, self._baudrate)

    def test_communication(self):

        try:
            test_package = self.drs.Read_ps_Model()
            print(test_package)
            if (test_package[0] == 0) and (test_package[1] == 17) and (test_package[2] == 512) and (test_package[3] == 10) and (test_package[4] == 227):
                print('TRUE')
                return True

            print('FALSE')
            return False

        except:
            print('EXCEPT')
            return False

    def _calib_sequence(self):

        print('\n  Valeeendoooo!! \n')

        time.clock()

        print(self.serial_list)

        #######################
        # Plot initialization #
        #######################

        fig = plt.figure()

        # HRADC samples
        ax1   = fig.add_subplot(2,2,1)
        ax1.ticklabel_format(useOffset = False)
        ax1.set_ylabel('HRADC Samples [LSB]')
        ax1.grid()

        # Samples histogram
        ax2   = fig.add_subplot(2,2,2)
        ax2.ticklabel_format(useOffset = False)

        ax3   = fig.add_subplot(2,2,3)    # HRADC mean Vs DMM mean
        ax3_2 = ax3.twinx()
        ax4   = fig.add_subplot(2,2,4)    # HRADC std Vs DMM std
        ax4_2 = ax4.twinx()

        self.nHRADC = 4 - self.serial_list.count(None)
        print('\n*** ' + str(self.nHRADC) + ' placas HRADC serão calibradas ***\n')

        print('Configurando nHRADC...\n')
        self.update_gui.emit('Configurando nHRADC...')
        self.drs.Config_nHRADC(self.nHRADC)
        time.sleep(1)

        print('Resetando HRADC...\n')
        self.update_gui.emit('Resetando nHRADC...')
        self.drs.ResetHRADCBoards(1)
        time.sleep(1)
        self.drs.ResetHRADCBoards(0)
        time.sleep(1)

        print('Configurando backplane...\n')
        self.update_gui.emit('Configurando backplane...')
        self.drs.SelectHRADCBoard(0)
        time.sleep(0.5)
        self.drs.SelectTestSource('Vin_bipolar')
        time.sleep(0.5)

        print('Configurando placas em Vref_bipolar_p...\n')
        self.update_gui.emit('Configurando placas em Vref_bipolar_p...')
        for slot in range(self.nHRADC):
            self.drs.ConfigHRADC(slot, 100000, 'Vref_bipolar_p', 0, 0)
            time.sleep(1)

        print('Iniciando warm-up...\n')
        self.update_gui.emit('Iniciando warm-up...')
        self.drs.EnableHRADCSampling()

        t = Timer(10,self._timeout)
        t.start()

        while(t.is_alive()):
            print(time.strftime("%H:%M:%S", time.gmtime()))
            time.sleep(1)
        self.drs.DisableHRADCSampling()
        time.sleep(1)

        #########################
        #### ITERAR AQUI!!! #####
        #########################

        slot = 0

        print('************ SLOT ' + str(slot) + ' ************\n')

        log = HRADCLogCalib()
        ufmdata_16 = []
        emptyBuff = np.array([])

        log.serial_number_hradc = self.serial_list[slot]

        self.drs.SelectHRADCBoard(slot)
        time.sleep(0.5)
        self.drs.SelectTestSource('Vin_bipolar')
        time.sleep(0.5)

        print('Medindo +Vref...\n')
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)
        self.drs.EnableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableHRADCSampling()
        time.sleep(0.5)

        sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
        print(sampHRADC)

        if np.array_equal(sampHRADC,emptyBuff):
            print('\n************** FALHA SAMPLES BUFFER **************\n')
            self.source.DisableOutput()
            self.DisableHRADCSampling()
            return

        log.vref_p = self._convertVinSample(sampHRADC.mean())
        print('\n+Vref = ' + str(log.vref_p) + ' V\n')

        print('Medindo -Vref...\n')
        self.drs.ConfigHRADC(slot,100000,'Vref_bipolar_n',0,0)
        time.sleep(1)
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)
        self.drs.EnableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableHRADCSampling()
        time.sleep(0.5)

        sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
        print(sampHRADC)

        if np.array_equal(sampHRADC,emptyBuff):
            print('\n************** FALHA SAMPLES BUFFER **************\n')
            self.source.DisableOutput()
            self.DisableHRADCSampling()
            return

        log.vref_n = self._convertVinSample(sampHRADC.mean())
        print('\n-Vref = ' + str(log.vref_n) + ' V\n')

        print('Medindo GND...\n')
        self.drs.ConfigHRADC(slot,100000,'GND',0,0)
        time.sleep(1)
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)
        self.drs.EnableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableHRADCSampling()
        time.sleep(0.5)

        sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
        print(sampHRADC)

        if np.array_equal(sampHRADC,emptyBuff):
            print('\n************** FALHA SAMPLES BUFFER **************\n')
            self.source.DisableOutput()
            self.DisableHRADCSampling()
            return

        log.gnd = self._convertVinSample(sampHRADC.mean())
        print('\nGND = ' + str(log.gnd) + ' V\n')


        print('*****************************************')
        print('****** Iniciando calibração Vin... ******')
        print('*****************************************\n')

        self.drs.ConfigHRADC(slot,100000,'Vin_bipolar',0,0)
        time.sleep(1)
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)

        ################################################
        print('     *** Configurando Vin -FS ... ***\n')
        ################################################

        sourceOut = -10
        self.source.EnableOutput()

        while True:
            sourceOut = self._saturate(sourceOut,-10.2,10.2)

            # if any HRADC samples != 0, set source lower
            print('sourceOut = ' + str(sourceOut) + ' V\n')
            self.source.SetOutput(sourceOut,'V')
            time.sleep(self.settlingTime)

            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
            print(sampHRADC)

            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            deltaFS = meanHRADC*self.vin_lsb
            inc = deltaFS if deltaFS > self.vin_lsb else self.vin_lsb

            print('\nmax    meanHRADC   stdHRADC    inc')
            print(str(sampHRADC.max()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '    ' + str(inc) + '\n')

            if((sampHRADC == 0).all()):
                break

            sourceOut -= inc

        vin_negFS = np.array(self.dmm.ReadMeasurementPoints()).mean()
        print('Vin -FS: ' + str(vin_negFS) + ' V\n')

        #################################################
        print('\n     *** Procurando Vin T[1] ... ***\n')
        #################################################

        sumNonFSCodes = 0
        T_1 = vin_negFS

        while True:

            # Increment source output
            sourceOut += self.vin_step
            sourceOut = self._saturate(sourceOut,-10.2,10.2)
            print('sourceOut = ' + str(sourceOut) + ' V\n')
            self.source.SetOutput(sourceOut,'V')
            time.sleep(self.settlingTime)

            # Start measurements
            self.dmm.TrigMultipointMeas()
            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_allblocks())
            print(sampHRADC)

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            print('\nmax    meanHRADC   stdHRADC')
            print(str(sampHRADC.max()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '\n')


            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            #T_1 = np.array(DMM.ReadMeasurementPoints()).mean()
            old_T_1 = T_1
            T_1 = np.array(self.dmm.GetMultipointMeas()).mean()

            # Repeat if more than 50% HRADC samples == 0
            old_sumNonFSCodes = sumNonFSCodes
            sumNonFSCodes = sum(sampHRADC > 0)
            print('DMM T[1]     "non-FS codes"')
            print(str(T_1) + '      ' + str(sumNonFSCodes) + '\n')
            if(sumNonFSCodes >= len(sampHRADC)/2):
                break

        T_1 = (old_T_1*old_sumNonFSCodes + T_1*sumNonFSCodes)/(old_sumNonFSCodes + sumNonFSCodes)

        print('*** Vin T[1]: ' + str(T_1) + ' V ***\n\n')


        ################################################
        print('     *** Configurando Vin +FS ... ***\n')
        ################################################

        sourceOut = 10

        while True:
            sourceOut = self._saturate(sourceOut,-10.2,10.2)

            # if any HRADC samples != 0, set source lower
            print('sourceOut = ' + str(sourceOut) + ' V\n')
            self.source.SetOutput(sourceOut,'V')
            time.sleep(self.settlingTime)

            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
            print(sampHRADC)

            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            deltaFS = 20-meanHRADC*self.vin_lsb
            inc = deltaFS if deltaFS > self.vin_lsb else self.vin_lsb

            print('\nmin    meanHRADC   stdHRADC    inc')
            print(str(sampHRADC.min()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '    ' + str(inc) + '\n')

            if((sampHRADC == 0x3FFFF).all()):
                break

            sourceOut += inc

        vin_posFS = np.array(self.dmm.ReadMeasurementPoints()).mean()
        print('Vin +FS: ' + str(vin_posFS) + ' V\n')

        ###################################################
        print('\n     *** Procurando Vin T[end] ... ***\n')
        ###################################################

        sumNonFSCodes = 0
        T_end = vin_posFS

        while True:

            # Decrement source output
            sourceOut -= self.vin_step
            sourceOut = self._saturate(sourceOut,-10.2,10.2)
            print('sourceOut = ' + str(sourceOut) + ' V\n')
            self.source.SetOutput(sourceOut,'V')
            time.sleep(self.settlingTime)

            # Start measurements
            self.dmm.TrigMultipointMeas()
            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_allblocks())
            print(sampHRADC)

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            print('\nmin    meanHRADC   stdHRADC')
            print(str(sampHRADC.min()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '\n')


            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            #T_end = np.array(DMM.ReadMeasurementPoints()).mean()
            old_T_end = T_end
            T_end = np.array(self.dmm.GetMultipointMeas()).mean()

            # Repeat if more than 50% HRADC samples == 0
            old_sumNonFSCodes = sumNonFSCodes
            sumNonFSCodes = sum(sampHRADC < 0x3FFFF)
            print('DMM T[end]     "non-FS codes"')
            print(str(T_end) + '      ' + str(sumNonFSCodes) + '\n')
            if(sumNonFSCodes >= len(sampHRADC)/2):
                break

        T_end = (old_T_end*old_sumNonFSCodes + T_end*sumNonFSCodes)/(old_sumNonFSCodes + sumNonFSCodes)

        print('*** Vin T[end]: ' + str(T_end) + ' V ***')
        print('*** Vin T[1]: ' + str(T_1) + ' V ***\n')

        log.vin_gain = (T_end - T_1)/(20 - self.vin_lsb)
        log.vin_offset = T_1 - log.vin_gain*(-10 + self.vin_lsb/2)

        print('  Vin Gain: ' + str(log.vin_gain))
        print('  Vin Offset: ' + str(log.vin_offset))
        print('\nTempo de execução: ' + str(time.clock()/60) + ' min\n\n')

        self.source.SetOutput(0,'V')
        self.source.DisableOutput()
        self.drs.DisableHRADCSampling()
        time.sleep(1)

        print('**********************************')
        print('****** Medindo temperaturas ******')
        print('**********************************\n')

        self.update_gui.emit('Medindo temperaturas...')

        self.drs.ConfigHRADC(slot,100000,'Temp',0,0)
        time.sleep(1)
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)
        self.drs.EnableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableSamplesBuffer()
        time.sleep(0.5)
        self.drs.DisableHRADCSampling()
        time.sleep(0.5)

        sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))

        if np.array_equal(sampHRADC,emptyBuff):
            print('\n************** FALHA SAMPLES BUFFER **************\n')
            self.source.DisableOutput()
            self.DisableHRADCSampling()
            return

        log.temperature_hradc = -100*self._convertVinSample(sampHRADC.mean())
        log.temperature_power_supply = self.source.GetTemperature()
        log.temperature_dmm = self.dmm.GetTemperature()

        print('HRADC Temp = ' + str(log.temperature_hradc) + ' oC\n')
        print('Source Temp = ' + str(log.temperature_power_supply) + ' oC\n')
        print('DMM Temp = ' + str(log.temperature_dmm) + ' oC\n')


        print('*****************************************')
        print('****** Iniciando calibração Iin... ******')
        print('*****************************************\n')

        self.dmm.SetMeasurementType('DCI',0.05)
        self.source.SetOutput(0,'I')
        self.drs.SelectTestSource('Iin_bipolar')
        time.sleep(0.5)
        self.drs.ConfigHRADC(slot,100000,'Iin_bipolar',0,0)
        time.sleep(1)
        self.drs.EnableHRADCSampling()
        time.sleep(0.5)

        ################################################
        print('     *** Configurando Iin -FS ... ***\n')
        ################################################

        sourceOut = -0.0495
        self.source.EnableOutput()

        while True:
            sourceOut = self._saturate(sourceOut,-0.051,0.05)

            # if any HRADC samples != 0, set source lower
            print('sourceOut = ' + str(sourceOut) + ' A\n')
            self.source.SetOutput(sourceOut,'I')
            time.sleep(self.settlingTime)

            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
            print(sampHRADC)

            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            deltaFS = meanHRADC*self.iin_lsb
            inc = deltaFS if deltaFS > self.iin_lsb else self.iin_lsb

            print('\nmax    meanHRADC   stdHRADC    inc')
            print(str(sampHRADC.max()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '    ' + str(inc) + '\n')

            if((sampHRADC == 0).all()):
                break

            sourceOut -= inc

        iin_negFS = np.array(self.dmm.ReadMeasurementPoints()).mean()
        print('Iin -FS: ' + str(iin_negFS) + ' A\n')

        #################################################
        print('\n     *** Procurando Iin T[1] ... ***\n')
        #################################################

        sumNonFSCodes = 0
        T_1 = iin_negFS

        while True:

            # Increment source output
            sourceOut += self.iin_step
            sourceOut = self._saturate(sourceOut,-0.051,0.05)
            print('sourceOut = ' + str(sourceOut) + ' A\n')
            self.source.SetOutput(sourceOut,'I')
            time.sleep(self.settlingTime)

            # Start measurements
            self.dmm.TrigMultipointMeas()
            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_allblocks())
            print(sampHRADC)

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            print('\nmax    meanHRADC   stdHRADC')
            print(str(sampHRADC.max()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '\n')


            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            #T_1 = np.array(DMM.ReadMeasurementPoints()).mean()
            old_T_1 = T_1
            T_1 = np.array(self.dmm.GetMultipointMeas()).mean()

            # Repeat if more than 50% HRADC samples == 0
            old_sumNonFSCodes = sumNonFSCodes
            sumNonFSCodes = sum(sampHRADC > 0)
            print('DMM T[1]     "non-FS codes"')
            print(str(T_1) + '      ' + str(sumNonFSCodes) + '\n')
            if(sumNonFSCodes >= len(sampHRADC)/2):
                break

        T_1 = (old_T_1*old_sumNonFSCodes + T_1*sumNonFSCodes)/(old_sumNonFSCodes + sumNonFSCodes)

        print('*** Iin T[1]: ' + str(T_1) + ' A ***\n\n')


        ################################################
        print('     *** Configurando Iin +FS ... ***\n')
        ################################################

        sourceOut = 0.0495

        while True:
            sourceOut = self._saturate(sourceOut,-0.051,0.05)

            # if any HRADC samples != 0, set source lower
            print('sourceOut = ' + str(sourceOut) + ' A\n')
            self.source.SetOutput(sourceOut,'I')
            time.sleep(self.settlingTime)

            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_blocks(0))
            print(sampHRADC)

            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            deltaFS = 0.1-meanHRADC*self.iin_lsb
            inc = deltaFS if deltaFS > self.iin_lsb else self.iin_lsb

            print('\nmin    meanHRADC   stdHRADC    inc')
            print(str(sampHRADC.min()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '    ' + str(inc) + '\n')

            if((sampHRADC == 0x3FFFF).all()):
                break

            sourceOut += inc

        iin_posFS = np.array(self.dmm.ReadMeasurementPoints()).mean()
        print('Iin +FS: ' + str(iin_posFS) + ' A\n')

        ###################################################
        print('\n     *** Procurando Iin T[end] ... ***\n')
        ###################################################

        sumNonFSCodes = 0
        T_end = iin_posFS

        while True:

            # Decrement source output
            sourceOut -= self.iin_step
            sourceOut = self._saturate(sourceOut,-0.051,0.05)
            print('sourceOut = ' + str(sourceOut) + ' A\n')
            self.source.SetOutput(sourceOut,'I')
            time.sleep(self.settlingTime)

            # Start measurements
            self.dmm.TrigMultipointMeas()
            self.drs.EnableSamplesBuffer()
            time.sleep(1)
            self.drs.DisableSamplesBuffer()
            time.sleep(1)

            sampHRADC = np.array(self.drs.Recv_samplesBuffer_allblocks())
            print(sampHRADC)

            meanHRADC = sampHRADC.mean()
            stdHRADC = sampHRADC.std()

            print('\nmin    meanHRADC   stdHRADC')
            print(str(sampHRADC.min()) + '    ' + str(meanHRADC) + '    ' + str(stdHRADC) + '\n')


            if np.array_equal(sampHRADC,emptyBuff):
                print('\n************** FALHA SAMPLES BUFFER **************\n')
                self.source.DisableOutput()
                self.DisableHRADCSampling()
                return

            #T_end = np.array(DMM.ReadMeasurementPoints()).mean()
            old_T_end = T_end
            T_end = np.array(self.dmm.GetMultipointMeas()).mean()

            # Repeat if more than 50% HRADC samples == 0
            old_sumNonFSCodes = sumNonFSCodes
            sumNonFSCodes = sum(sampHRADC < 0x3FFFF)
            print('DMM T[end]     "non-FS codes"')
            print(str(T_end) + '      ' + str(sumNonFSCodes) + '\n')
            if(sumNonFSCodes >= len(sampHRADC)/2):
                break

        T_end = (old_T_end*old_sumNonFSCodes + T_end*sumNonFSCodes)/(old_sumNonFSCodes + sumNonFSCodes)

        print('*** Iin T[end]: ' + str(T_end) + ' A ***')
        print('*** Iin T[1]: ' + str(T_1) + ' A ***\n')

        log.iin_gain = (T_end - T_1)/(0.1 - self.iin_lsb)
        log.iin_offset = T_1 - log.iin_gain*(-0.05 + self.iin_lsb/2)

        print('  Iin Gain: ' + str(log.iin_gain))
        print('  Iin Offset: ' + str(log.iin_offset))
        print('\nTempo de execução: ' + str(time.clock()/60) + ' min\n\n')

        self.source.SetOutput(0,'V')
        self.source.DisableOutput()
        self.drs.DisableHRADCSampling()
        time.sleep(1)

        log_res = self._send_to_server(log)

        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo PowerModuleLog

        self.calib_complete.emit(log_res)

    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        print('client_data:\n')
        print(client_data)
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        server_status = self._parse_response(client_response)
        print(client_response)
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

    def _saturate(self,val,min,max):
        if val > max:
            return max
        elif val < min:
            return min
        return val

    def _convertVinSample(self,sample):
        val = (sample-131072)*self.vin_lsb
        return val

    def _convertIinSample(self,sample):
        val = (sample-131072)*self.iin_lsb
        return val

    def run(self):
        self._calib_sequence()
        #pass

if __name__ == '__main__':
    hradc = HRADCCalib()
    hradc.open_serial_port()
    #hradc._calib_sequence()

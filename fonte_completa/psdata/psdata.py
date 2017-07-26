import simplejson as json
from PyQt5.QtCore import pyqtSlot

class PowerSupply:

    def __init__(self, serial_number=None):
        self._serial_number = serial_number

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    def _get_power_supply_data(self):
        data = {}
        data['numero_serie'] = self._serial_number
        return data

    @property
    def data(self):
        return self._get_power_supply_data()

    @property
    def method(self):
        return "/AddPowerSupply"

class PowerSupplyLog:

    def __init__(self, id_canal_ps=None, test_result=None, serial_number_ps=None,
                    result_test_on_off=None, iout_add_20_duty_cycle=None,
                    iout_less_20_duty_cycle=None, iout0=None, iout1=None,
                    vout0=None, vout1=None, vdclink0=None, vdclink1=None,
                    temperatura0=None, temperatura1=None, details=None):

        self._id_canal_ps               = id_canal_ps
        self._test_result               = test_result
        self._serial_number_ps          = serial_number_ps
        self._result_test_on_off        = result_test_on_off
        self._iout_add_20_duty_cycle    = iout_add_20_duty_cycle
        self._iout_less_20_duty_cycle   = iout_less_20_duty_cycle
        self._iout0                     = iout0
        self._iout1                     = iout1
        self._vout0                     = vout0
        self._vout1                     = vout1
        self._vdclink0                  = vdclink0
        self._vdclink1                  = vdclink1
        self._temperatura0              = temperatura0
        self._temperatura1              = temperatura1
        self._details                   = details

    @property
    def id_canal_power_supply(self):
        return self._id_canal_ps

    @id_canal_power_supply.setter
    def id_canal_power_supply(self, value):
        self._id_canal_ps = value

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_power_supply(self):
        return self._serial_number_ps

    @serial_number_power_supply.setter
    def serial_number_power_supply(self, value):
        self._serial_number_ps = value

    @property
    def result_test_on_off(self):
        return self._result_test_on_off

    @result_test_on_off.setter
    def result_test_on_off(self, value):
        self._result_test_on_off = value

    @property
    def iout_add_20_duty_cycle(self):
        return self._iout_add_20_duty_cycle

    @iout_add_20_duty_cycle.setter
    def iout_add_20_duty_cycle(self, value):
        self._iout_add_20_duty_cycle = value

    @property
    def iout_less_20_duty_cycle(self):
        return self._iout_less_20_duty_cycle

    @iout_less_20_duty_cycle.setter
    def iout_less_20_duty_cycle(self, value):
        self._iout_less_20_duty_cycle = value

    @property
    def iout0(self):
        return self._iout0

    @iout0.setter
    def iout0(self, value):
        self._iout0 = value

    @property
    def iout1(self):
        return self._iout1

    @iout1.setter
    def iout1(self, value):
        self._iout1 = value

    @property
    def vout0(self):
        return self._vout0

    @vout0.setter
    def vout0(self, value):
        self._vout0 = value

    @property
    def vout1(self):
        return self._vout1

    @vout1.setter
    def vout1(self, value):
        self._vout1 = value

    @property
    def vdclink0(self):
        return self._vdclink0

    @vdclink0.setter
    def vdclink0(self, value):
        self._vdclink0 = value

    @property
    def vdclink1(self):
        return self._vdclink1

    @vdclink1.setter
    def vdclink1(self, value):
        self._vdclink1 = value

    @property
    def temperatura0(self):
        return self._temperatura0

    @temperatura0.setter
    def temperatura0(self, value):
        self._temperatura0 = value

    @property
    def temperatura1(self):
        return self._temperatura1

    @temperatura1.setter
    def temperatura1(self, value):
        self._temperatura1 = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_ps_log_data(self):
        data = {}
        data['id_canal_fonte']              = self._id_canal_ps
        data['resultado_teste']             = self._test_result
        data['numero_serie_fonte']          = self._serial_number_ps
        data['resultado_teste_on_off']      = self._result_test_on_off
        data['iout_mais_20_duty_cycle']     = self._iout_add_20_duty_cycle
        data['iout_menos_20_duty_cycle']    = self._iout_less_20_duty_cycle
        data['iout0']                       = self._iout0
        data['iout1']                       = self._iout1
        data['vout0']                       = self._vout0
        data['vout1']                       = self._vout1
        data['vdclink0']                    = self._vdclink0
        data['vdclink1']                    = self._vdclink1
        data['temperatura0']                = self._temperatura0
        data['temperatura1']                = self._temperatura1
        data['details']                     = self._details
        return data

    @property
    def data(self):
        return self._get_ps_log_data()

    @property
    def method(self):
        return "/AddLogPowerSupply"

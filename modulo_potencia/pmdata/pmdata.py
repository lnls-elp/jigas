from elpwebclient import *
import simplejson as json
from PyQt5.QtCore import pyqtSlot

class PowerModule:

    def __init__(self, serial_number=None):
        self._serial_number = serial_number

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    def _get_power_module_data(self):
        data = {}
        data['numero_serie'] = self._serial_number
        return data

    @property
    def data(self):
        return self._get_power_module_data()

    @property
    def method(self):
        return "/AddPowerModule"

class PowerModuleLog:

    def __init__(self, test_result=None, serial_number_power_module=None, iload0=None,
                    iload1=None, iload2=None, iload3=None, iload4=None, iload5=None,
                    iload6=None, iload7=None, iload8=None, iload9=None, iload10=None,
                    details=None):

        self._test_result   = test_result
        self._serial_number_power_module = serial_number_dcct
        self._iload0            = iload0
        self._iload1            = iload1
        self._iload2            = iload2
        self._iload3            = iload3
        self._iload4            = iload4
        self._iload5            = iload5
        self._iload6            = iload6
        self._iload7            = iload7
        self._iload8            = iload8
        self._iload9            = iload9
        self._iload10           = iload10
        self._details           = details

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_power_module(self):
        return self._serial_number_power_module

    @serial_number_power_module.setter
    def serial_number_power_module(self, value):
        self._serial_number_power_module = value

    @property
    def iload0(self):
        return self._iload0

    @iload0.setter
    def iload0(self, value):
        self._iload0 = value

    @property
    def iload1(self):
        return self._iload1

    @iload1.setter
    def iload1(self, value):
        self._iload1 = value

    @property
    def iload2(self):
        return self._iload2

    @iload2.setter
    def iload2(self, value):
        self._iload2 = value

    @property
    def iload3(self):
        return self._iload3

    @iload3.setter
    def iload3(self, value):
        self._iload3 = value

    @property
    def iload4(self):
        return self._iload4

    @iload4.setter
    def iload4(self, value):
        self._iload4 = value

    @property
    def iload5(self):
        return self._iload5

    @iload5.setter
    def iload5(self, value):
        self._iload5 = value

    @property
    def iload6(self):
        return self._iload6

    @iload6.setter
    def iload6(self, value):
        self._iload6 = value

    @property
    def iload7(self):
        return self._iload7

    @iload7.setter
    def iload7(self, value):
        self._iload2 = value

    @property
    def iload8(self):
        return self._iload8

    @iload8.setter
    def iload8(self, value):
        self._iload8 = value

    @property
    def iload9(self):
        return self._iload9

    @iload9.setter
    def iload9(self, value):
        self._iload9 = value

    @property
    def iload10(self):
        return self._iload10

    @iload10.setter
    def iload10(self, value):
        self._iload10 = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_power_module_log_data(self):
        data = {}
        data['resultado_teste']     = self._test_result
        data['numero_serie_dcct']   = self._serial_number_power_module
        data['iload0']              = self._iload0
        data['iload1']              = self._iload1
        data['iload2']              = self._iload2
        data['iload3']              = self._iload3
        data['iload4']              = self._iload4
        data['iload5']              = self._iload5
        data['iload6']              = self._iload6
        data['iload7']              = self._iload7
        data['iload8']              = self._iload8
        data['iload9']              = self._iload9
        data['iload10']             = self._iload10
        data['details']             = self._details
        return data

    @property
    def data(self):
        return self._get_power_module_log_data()

    @property
    def method(self):
        return "/AddLogPowerModule"

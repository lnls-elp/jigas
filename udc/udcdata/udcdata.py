from elpwebclient import *
import simplejson as json
from PyQt5.QtCore import pyqtSlot

class UDC:

    def __init__(self, serial_number=None, variant=None):
        self._serial_number = serial_number

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    def _get_udc_data(self):
        data = {}
        data['numero_serie']    = self._serial_number
        return data

    @property
    def data(self):
        return self._get_udc_data()

    @property
    def method(self):
        return "/AddUdc"

class UDCLog:

    def __init__(self, test_result=None, serial_number_udc=None, details=None):

        self._test_result           = test_result
        self._serial_number_udc     = serial_number_udc
        self._details               = details

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_udc(self):
        return self._serial_number_udc

    @serial_number_udc.setter
    def serial_number_udc(self, value):
        self._serial_number_udc = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_udc_log_data(self):
        data = {}
        data['resultado_teste']     = self._test_result
        data['numero_serie_udc']    = self._serial_number_udc
        data['details']             = self._details
        return data

    @property
    def data(self):
        return self._get_udc_log_data()

    @property
    def method(self):
        return "/AddLogUdc"

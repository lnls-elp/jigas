from elpwebclient import *
import simplejson as json

class DCCT:

    def __init__(self, serial_number):
        self._serial_number = serial_number

    @property
    def serial_number(self):
        return self._serial_number

    def _get_dcct_data(self):
        data = {}
        data['numero_serie'] = self._serial_number
        return data

    def add_dcct(self):
        client = ElpWebClient()
        data = self._get_dcct_data()
        method = "/AddDcct"
        response = client.do_request(method, data)
        return response

class DcctLog:

    def __init__(self, resultado_teste, numero_serie_dcct, iload0, iload1, iload2,
                    iload3, iload4, iload5, iload6, iload7, iload8, iload9, iload10):
        self._resultado_teste   = resultado_teste
        self._numero_serie_dcct = numero_serie_dcct
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

    def _get_dcct_log_data(self):
        data = {}
        data['resultado_teste']     = self._resultado_teste
        data['numero_serie_dcct']   = self._numero_serie_dcct
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
        return data

    def add_log_dcct(self):
        client = ElpWebClient()
        data = self._get_dcct_log_data()
        method = '/AddLogDcct'
        response = client.do_request(method, data)
        return response

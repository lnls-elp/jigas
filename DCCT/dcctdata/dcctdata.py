from elpwebclient import *
import simplejson as json

class DCCT:

    def __init__(self, numero_serie=None):
        self._serial_number = numero_serie

    @property
    def numero_serie(self):
        return self._serial_number

    @numero_serie.setter
    def numero_serie(self, value):
        self._serial_number = value

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

class DCCTLog:

    def __init__(self, resultado_teste=None, numero_serie_dcct=None, iload0=None,
                    iload1=None, iload2=None, iload3=None, iload4=None, iload5=None,
                    iload6=None, iload7=None, iload8=None, iload9=None, iload10=None):

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

    @property
    def resultado_teste(self):
        return self._resultado_teste

    @resultado_teste.setter
    def resultado_teste(self, value):
        self._resultado_teste = value

    @property
    def numero_serie_dcct(self):
        return self._numero_serie_dcct

    @numero_serie_dcct.setter
    def numero_serie_dcct(self, value):
        self._numero_serie_dcct = value

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

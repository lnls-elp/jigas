class DCCT:

    def __init__(self, serial_number=None, variant=None):
        self._serial_number = serial_number
        self._variant       = variant

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def variant(self):
        return self._variant

    @variant.setter
    def variant(self, value):
        self._variant = value

    def _get_dcct_data(self):
        data = {}
        data['numero_serie']    = self._serial_number
        data['variante']        = self._variant
        return data

    @property
    def data(self):
        return self._get_dcct_data()

    @property
    def method(self):
        return "/AddDcct"

class DCCTLog:

    def __init__(self):

        self._id_canal_dcct         = None
        self._test_result           = None
        self._serial_number_dcct    = None
        self._iload_off             = None
        self._iload0                = None
        self._iload1                = None
        self._iload2                = None
        self._iload3                = None
        self._iload4                = None
        self._iload5                = None
        self._iload6                = None
        self._iload7                = None
        self._iload8                = None
        self._iload9                = None
        self._iload10               = None
        self._details               = None

    @property
    def id_canal_dcct(self):
        return self._test_result

    @id_canal_dcct.setter
    def id_canal_dcct(self, value):
        self._id_canal_dcct = value

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_dcct(self):
        return self._serial_number_dcct

    @serial_number_dcct.setter
    def serial_number_dcct(self, value):
        self._serial_number_dcct = value

    @property
    def iload_off(self):
        return self._iload_off

    @iload_off.setter
    def iload_off(self, value):
        self._iload_off = value

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
        self._iload7 = value

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

    def _get_dcct_log_data(self):
        data = {}
        data['id_canal_dcct']       = self._id_canal_dcct
        data['resultado_teste']     = self._test_result
        data['numero_serie_dcct']   = self._serial_number_dcct
        data['iload_desligado']     = self._iload_off
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
        return self._get_dcct_log_data()

    @property
    def method(self):
        return "/AddLogDcct"

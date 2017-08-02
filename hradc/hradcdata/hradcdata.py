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

    def __init__(self):

        self._test_result                   = None
        self._serial_number_power_module    = None
        self._iload0                        = None
        self._iload1                        = None
        self._iload2                        = None
        self._iload3                        = None
        self._iload4                        = None
        self._iload5                        = None
        self._vload0                        = None
        self._vload1                        = None
        self._vload2                        = None
        self._vload3                        = None
        self._vload4                        = None
        self._vload5                        = None
        self._vdclink0                      = None
        self._vdclink1                      = None
        self._vdclink2                      = None
        self._vdclink3                      = None
        self._vdclink4                      = None
        self._vdclink5                      = None
        self._temperatura0                  = None
        self._temperatura1                  = None
        self._temperatura2                  = None
        self._temperatura3                  = None
        self._temperatura4                  = None
        self._temperatura5                  = None
        self._details                       = None

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
    def vload0(self):
        return self._vload0

    @vload0.setter
    def vload0(self, value):
        self._vload0 = value

    @property
    def vload1(self):
        return self._vload1

    @vload1.setter
    def vload1(self, value):
        self._vload1 = value

    @property
    def vload2(self):
        return self._vload2

    @vload2.setter
    def vload2(self, value):
        self._vload2 = value

    @property
    def vload3(self):
        return self._vload3

    @vload3.setter
    def vload3(self, value):
        self._vload3 = value

    @property
    def vload4(self):
        return self._vload4

    @vload4.setter
    def vload4(self, value):
        self._vload4 = value

    @property
    def vload5(self):
        return self._vload5

    @vload5.setter
    def vload5(self, value):
        self._vload5 = value

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
    def vdclink2(self):
        return self._vdclink2

    @vdclink2.setter
    def vdclink2(self, value):
        self._vdclink2 = value

    @property
    def vdclink3(self):
        return self._vdclink3

    @vdclink3.setter
    def vdclink3(self, value):
        self._vdclink3 = value

    @property
    def vdclink4(self):
        return self._vdclink4

    @vdclink4.setter
    def vdclink4(self, value):
        self._vdclink4 = value

    @property
    def vdclink5(self):
        return self._vdclink5

    @vdclink5.setter
    def vdclink5(self, value):
        self._vdclink5 = value

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
    def temperatura2(self):
        return self._temperatura2

    @temperatura2.setter
    def temperatura2(self, value):
        self._temperatura2 = value

    @property
    def temperatura3(self):
        return self._temperatura3

    @temperatura3.setter
    def temperatura3(self, value):
        self._temperatura3 = value

    @property
    def temperatura4(self):
        return self._temperatura4

    @temperatura4.setter
    def temperatura4(self, value):
        self._temperatura4 = value

    @property
    def temperatura5(self):
        return self._temperatura5

    @temperatura5.setter
    def temperatura5(self, value):
        self._temperatura5 = value

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
        data['vload0']              = self._vload0
        data['vload1']              = self._vload1
        data['vload2']              = self._vload2
        data['vload3']              = self._vload3
        data['vload4']              = self._vload4
        data['vload5']              = self._vload5
        data['vdclink0']            = self._vdclink0
        data['vdclink1']            = self._vdclink1
        data['vdclink2']            = self._vdclink2
        data['vdclink3']            = self._vdclink3
        data['vdclink4']            = self._vdclink4
        data['vdclink5']            = self._vdclink5
        data['temperatura0']        = self._temperatura0
        data['temperatura1']        = self._temperatura1
        data['temperatura2']        = self._temperatura2
        data['temperatura3']        = self._temperatura3
        data['temperatura4']        = self._temperatura4
        data['temperatura5']        = self._temperatura5
        data['details']             = self._details
        return data

    @property
    def data(self):
        return self._get_power_module_log_data()

    @property
    def method(self):
        return "/AddLogPowerModule"

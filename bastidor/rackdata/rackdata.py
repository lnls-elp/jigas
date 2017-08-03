class Rack:

    def __init__(self, serial_number=None):
        self._serial_number = serial_number

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    def _get_rack_data(self):
        data = {}
        data['numero_serie'] = self._serial_number
        return data

    @property
    def data(self):
        return self._get_rack_data()

    @property
    def method(self):
        return "/AddRack"

class RackLog:

    def __init__(self):

        self._test_result           = None
        self._serial_number_rack    = None
        self._iout0                 = None
        self._iout1                 = None
        self._iout2                 = None
        self._iout3                 = None
        self._delta_iout0           = None
        self._delta_iout1           = None
        self._delta_iout2           = None
        self._delta_iout3           = None
        self._details               = None

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_rack(self):
        return self._serial_number_rack

    @serial_number_rack.setter
    def serial_number_rack(self, value):
        self._serial_number_rack = value

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
    def iout2(self):
        return self._iout2

    @iout2.setter
    def iout2(self, value):
        self._iout2 = value

    @property
    def iout3(self):
        return self._iout3

    @iout3.setter
    def iout3(self, value):
        self._iout3 = value

    @property
    def delta_iout0(self):
        return self._delta_iout0

    @delta_iout0.setter
    def delta_iout0(self, value):
        self._delta_iout0 = value

    @property
    def delta_iout1(self):
        return self._delta_iout1

    @delta_iout1.setter
    def delta_iout1(self, value):
        self._delta_iout1 = value

    @property
    def delta_iout2(self):
        return self._delta_iout2

    @delta_iout2.setter
    def delta_iout2(self, value):
        self._delta_iout2 = value

    @property
    def delta_iout3(self):
        return self._delta_iout3

    @delta_iout3.setter
    def delta_iout3(self, value):
        self._delta_iout3 = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_rack_log_data(self):
        data = {}
        data['resultado_teste']     = self._test_result
        data['numero_serie_bastidor']   = self._serial_number_rack
        data['iout0']               = self._iout0
        data['iout1']               = self._iout1
        data['iout2']               = self._iout2
        data['iout3']               = self._iout3
        data['delta_iout0']         = self._delta_iout0
        data['delta_iout1']         = self._delta_iout1
        data['delta_iout2']         = self._delta_iout2
        data['delta_iout3']         = self._delta_iout3
        data['details']             = self._details
        return data

    @property
    def data(self):
        return self._get_rack_log_data()

    @property
    def method(self):
        return "/AddLogRack"

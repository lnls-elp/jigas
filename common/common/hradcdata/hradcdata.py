class HRADC:

    def __init__(self, serial_number=None):
        self._serial_number = serial_number
        self._variant = ""
        self._burden_res = 0.0
        self._cut_frequency = 0.0
        self._filter_order = 0
        self._temp_controller = 0
        self._burden_amplifier = ""
        self._gnd_jumper = False
        self._burden_jumper = False
        self._common_mode_filter = False

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

    @property
    def burden_resistor(self):
        return self._burden_res

    @burden_resistor.setter
    def burden_resistor(self, value):
        self._burden_res = value

    @property
    def cut_frequency(self):
        return self._cut_frequency

    @cut_frequency.setter
    def cut_frequency(self, value):
        self._cut_frequency = value

    @property
    def filter_order(self):
        return self._filter_order

    @filter_order.setter
    def filter_order(self, value):
        self._filter_order = value

    @property
    def temperature_controller(self):
        return self._temp_controller

    @temperature_controller.setter
    def temperature_controller(self, value):
        self._temp_controller = value

    @property
    def burden_amplifier(self):
        return self._burden_amplifier

    @burden_amplifier.setter
    def burden_amplifier(self, value):
        self._burden_amplifier = value

    @property
    def gnd_jumper(self):
        return self._gnd_jumper

    @gnd_jumper.setter
    def gnd_jumper(self, value):
        self._gnd_jumper = value

    @property
    def burden_jumper(self):
        return self._burden_jumper

    @burden_jumper.setter
    def burden_jumper(self, value):
        self._burden_jumper = value

    @property
    def common_mode_filter(self):
        return self._common_mode_filter

    @common_mode_filter.setter
    def common_mode_filter(self, value):
        self._common_mode_filter = value

    def _get_hradc_data(self):
        data = {}
        data['numero_serie']            = self._serial_number
        data['variante']                = self._variant
        data['resistor_burden']         = self._burden_res
        data['frequencia_corte']        = self._cut_frequency
        data['ordem_filtro']            = self._filter_order
        data['controlador_temperatura'] = self._temp_controller
        data['amplificador_burden']     = self._burden_amplifier
        data['jumper_gnd']              = self._gnd_jumper
        data['jumper_burden']           = self._burden_jumper
        data['filtro_modo_comum']       = self._common_mode_filter
        return data

    @property
    def data(self):
        return self._get_hradc_data()

    @property
    def method(self):
        return "/AddHradc"

class HRADCLog:

    def __init__(self):

        self._test_result           = None
        self._serial_number_hradc   = None
        self._device                = None
        self._gnd                   = 0.0
        self._vref_p                = 0.0
        self._vref_n                = 0.0
        self._temperature           = 0.0
        self._vin_p                 = 0.0
        self._vin_n                 = 0.0
        self._lin_p                 = 0.0
        self._lin_n                 = 0.0
        self._details               = ""

    @property
    def test_result(self):
        return self._test_result

    @test_result.setter
    def test_result(self, value):
        self._test_result = value

    @property
    def serial_number_hradc(self):
        return self._serial_number_hradc

    @serial_number_hradc.setter
    def serial_number_hradc(self, value):
        self._serial_number_hradc = value

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, value):
        self._device = value

    @property
    def gnd(self):
        return self._gnd

    @gnd.setter
    def gnd(self, value):
        self._gnd = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def vref_p(self):
        return self._vref_p

    @vref_p.setter
    def vref_p(self, value):
        self._vref_p = value

    @property
    def vref_n(self):
        return self._vref_n

    @vref_n.setter
    def vref_n(self, value):
        self._vref_n = value

    @property
    def vin_p(self):
        return self._vin_p

    @vin_p.setter
    def vin_p(self, value):
        self._vin_p = value

    @property
    def vin_n(self):
        return self._vin_n

    @vin_n.setter
    def vin_n(self, value):
        self._vin_n = value

    @property
    def lin_p(self):
        return self._lin_p

    @lin_p.setter
    def lin_p(self, value):
        self._lin_p = value

    @property
    def lin_n(self):
        return self._lin_n

    @lin_n.setter
    def lin_n(self, value):
        self._lin_n = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_hradc_log_data(self):
        data = {}
        data['resultado_teste']     = self._test_result
        data['numero_serie_hradc']  = self._serial_number_hradc
        data['id_medida']           = self._device
        data['gnd']                 = self._gnd
        data['vref_p']              = self._vref_p
        data['vref_n']              = self._vref_n
        data['temperature']         = self._temperature
        data['vin_p']               = self._vin_p
        data['vin_n']               = self._vin_n
        data['lin_p']               = self._lin_p
        data['lin_n']               = self._lin_n
        data['details']             = self._details
        return data

    @property
    def data(self):
        return self._get_hradc_log_data()

    @property
    def method(self):
        return "/AddLogHradc"

class HRADCLogCalib:

    def __init__(self):

        self._serial_number_hradc   = None
        self._temp_hradc            = 0.0
        self._temp_dmm              = 0.0
        self._temp_power_supply     = 0.0
        self._vin_gain              = 0.0
        self._vin_offset            = 0.0
        self._lin_gain              = 0.0
        self._lin_offset            = 0.0
        self._vref_p                = 0.0
        self._vref_n                = 0.0
        self._gnd                   = 0.0

    @property
    def serial_number_hradc(self):
        return self._serial_number_hradc

    @serial_number_hradc.setter
    def serial_number_hradc(self, value):
        self._serial_number_hradc = value

    @property
    def temperature_hradc(self):
        return self._temp_hradc

    @temperature_hradc.setter
    def temperature_hradc(self, value):
        self._temp_hradc = value

    @property
    def temperature_dmm(self):
        return self._temp_dmm

    @temperature_dmm.setter
    def temperature_dmm(self, value):
        self._temp_dmm = value

    @property
    def temperature_power_supply(self):
        return self._temp_power_supply

    @temperature_power_supply.setter
    def temperature_power_supply(self, value):
        self._temp_power_supply = value

    @property
    def vin_gain(self):
        return self._vin_gain

    @vin_gain.setter
    def vin_gain(self, value):
        self._vin_gain = value

    @property
    def vin_offset(self):
        return self._vin_offset

    @vin_offset.setter
    def vin_offset(self, value):
        self._vin_offset = value

    @property
    def lin_gain(self):
        return self._lin_gain

    @lin_gain.setter
    def lin_gain(self, value):
        self._lin_gain = value

    @property
    def lin_offset(self):
        return self._lin_offset

    @lin_offset.setter
    def lin_offset(self, value):
        self._lin_offset = value

    @property
    def vref_p(self):
        return self._vref_p

    @vref_p.setter
    def vref_p(self, value):
        self._vref_p = value

    @property
    def vref_n(self):
        return self._vref_n

    @vref_n.setter
    def vref_n(self, value):
        self._vref_n = value

    @property
    def gnd(self):
        return self._gnd

    @gnd.setter
    def gnd(self, value):
        self._gnd = value

    def _get_hradc_calib_data(self):
        data = {}
        data['numero_serie_hradc']  = self._serial_number_hradc
        data['temperatura_hradc']   = self._temp_hradc
        data['temperatura_dmm']     = self._temp_dmm
        data['temperatura_fonte']   = self._temp_power_supply
        data['ganho_vin']           = self._vin_gain
        data['offset_vin']          = self._vin_offset
        data['ganho_lin']           = self._lin_gain
        data['offset_lin']          = self._lin_offset
        data['vref_p']              = self._vref_p
        data['vref_n']              = self._vref_n
        data['gnd']                 = self._gnd
        return data

    @property
    def data(self):
        return self._get_hradc_calib_data()

    @property
    def method(self):
        return "/AddCalibHradc"

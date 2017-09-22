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

    def __init__(self):

        self._test_result                   = None
        self._serial_number_udc             = None
        self._io_expander                   = ""
        self._leds                          = ""
        self._buzzer                        = ""
        self._eeprom                        = ""
        self._flash                         = ""
        self._ram                           = ""
        self._rtc                           = ""
        self._temperature_sensor            = ""
        self._control_aliment_isol_plane    = ""
        self._uart                          = ""
        self._sdcard                        = ""
        self._ethernet_initizalization      = ""
        self._ethernet_ping                 = ""
        self._loopback                      = ""
        self._details                       = ""
        self._adc_ch_1                      = ""
        self._adc_ch_2                      = ""
        self._adc_ch_3                      = ""
        self._adc_ch_4                      = ""
        self._adc_ch_5                      = ""
        self._adc_ch_6                      = ""
        self._adc_ch_7                      = ""
        self._adc_ch_8                      = ""

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
    def io_expander(self):
        return self._io_expander

    @io_expander.setter
    def io_expander(self, value):
        self._io_expander = value

    @property
    def leds(self):
        return self._leds

    @leds.setter
    def leds(self, value):
        self._leds = value

    @property
    def buzzer(self):
        return self._buzzer

    @buzzer.setter
    def buzzer(self, value):
        self._buzzer = value

    @property
    def eeprom(self):
        return self._eeprom

    @eeprom.setter
    def eeprom(self, value):
        self._eeprom = value

    @property
    def flash(self):
        return self._flash

    @flash.setter
    def flash(self, value):
        self._flash = value

    @property
    def ram(self):
        return self._ram

    @ram.setter
    def ram(self, value):
        self._ram = value

    @property
    def rtc(self):
        return self._rtc

    @rtc.setter
    def rtc(self, value):
        self._rtc = value

    @property
    def temperature_sensor(self):
        return self._temperature_sensor

    @temperature_sensor.setter
    def temperature_sensor(self, value):
        self._temperature_sensor = value

    @property
    def control_aliment_isol_plane(self):
        return self._control_aliment_isol_plane

    @control_aliment_isol_plane.setter
    def control_aliment_isol_plane(self, value):
        self._control_aliment_isol_plane = value

    @property
    def uart(self):
        return self._uart

    @uart.setter
    def uart(self, value):
        self._uart = value

    @property
    def sdcard(self):
        return self._sdcard

    @sdcard.setter
    def sdcard(self, value):
        self._sdcard = value

    @property
    def ethernet_initialization(self):
        return self._ethernet_initizalization

    @ethernet_initialization.setter
    def ethernet_initialization(self, value):
        self._ethernet_initizalization = value

    @property
    def ethernet_ping(self):
        return self._ethernet_ping

    @ethernet_ping.setter
    def ethernet_ping(self, value):
        self._ethernet_ping = value

    @property
    def loopback(self):
        return self._loopback

    @loopback.setter
    def loopback(self, value):
        self._loopback = value

    @property
    def adc_ch_1(self):
        return self._adc_ch_1

    @adc_ch_1.setter
    def adc_ch_1(self, value):
        self._adc_ch_1 = value

    @property
    def adc_ch_2(self):
        return self._adc_ch_2

    @adc_ch_2.setter
    def adc_ch_2(self, value):
        self._adc_ch_2 = value

    @property
    def adc_ch_3(self):
        return self._adc_ch_3

    @adc_ch_3.setter
    def adc_ch_3(self, value):
        self._adc_ch_3 = value

    @property
    def adc_ch_4(self):
        return self._adc_ch_4

    @adc_ch_4.setter
    def adc_ch_4(self, value):
        self._adc_ch_4 = value

    @property
    def adc_ch_5(self):
        return self._adc_ch_5

    @adc_ch_5.setter
    def adc_ch_5(self, value):
        self._adc_ch_5 = value

    @property
    def adc_ch_6(self):
        return self._adc_ch_6

    @adc_ch_6.setter
    def adc_ch_6(self, value):
        self._adc_ch_6 = value

    @property
    def adc_ch_7(self):
        return self._adc_ch_7

    @adc_ch_7.setter
    def adc_ch_7(self, value):
        self._adc_ch_7 = value

    @property
    def adc_ch_8(self):
        return self._adc_ch_8

    @adc_ch_8.setter
    def adc_ch_8(self, value):
        self._adc_ch_8 = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_udc_log_data(self):
        data = {}
        data['resultado_teste']                 = self._test_result
        data['numero_serie_udc']                = self._serial_number_udc
        data['io_expander']                     = self._io_expander
        data['leds']                            = self._leds
        data['buzzer']                          = self._buzzer
        data['eeprom']                          = self._eeprom
        data['flash']                           = self._flash
        data['ram']                             = self._ram
        data['rtc']                             = self._rtc
        data['sensor_temperatura']              = self._temperature_sensor
        data['control_aliment_plano_isolado']   = self._control_aliment_isol_plane
        data['uart']                            = self._uart
        data['sdcard']                          = self._sdcard
        data['ethernet_inicializacao']          = self._ethernet_initizalization
        data['ethernet_ping']                   = self._ethernet_ping
        data['loopback']                        = self._loopback
        data['adc_ch_1']                        = self._adc_ch_1
        data['adc_ch_2']                        = self._adc_ch_2
        data['adc_ch_3']                        = self._adc_ch_3
        data['adc_ch_4']                        = self._adc_ch_4
        data['adc_ch_5']                        = self._adc_ch_5
        data['adc_ch_6']                        = self._adc_ch_6
        data['adc_ch_7']                        = self._adc_ch_7
        data['adc_ch_8']                        = self._adc_ch_8
        data['details']                         = self._details
        return data

    @property
    def data(self):
        return self._get_udc_log_data()

    @property
    def method(self):
        return "/AddLogUdc"

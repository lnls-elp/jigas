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

    def __init__(self, test_result=None, serial_number_udc=None, io_expander = None,
                leds=None, buzzer=None, eeprom=None, flash=None, ram=None,
                rtc_communication=None, rtc_interrupt=None, temperature_sensor=None,
                control_aliment_isol_plane=None, rs485=None, details=None):

        self._test_result                   = test_result
        self._serial_number_udc             = serial_number_udc
        self._io_expander                   = io_expander
        self._leds                          = leds
        self._buzzer                        = buzzer
        self._eeprom                        = eeprom
        self._flash                         = flash
        self._ram                           = ram
        self._rtc_communication             = rtc_communication
        self._rtc_interrupt                 = rtc_interrupt
        self._temperature_sensor            = temperature_sensor
        self._control_aliment_isol_plane    = control_aliment_isol_plane
        self._rs485                         = rs485
        self._details                       = details

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
    def rtc_communication(self):
        return self._rtc_communication

    @rtc_communication.setter
    def rtc_communication(self, value):
        self._rtc_communication = value

    @property
    def rtc_interrupt(self):
        return self._rtc_interrupt

    @rtc_interrupt.setter
    def rtc_interrupt(self, value):
        self._rtc_interrupt = value

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

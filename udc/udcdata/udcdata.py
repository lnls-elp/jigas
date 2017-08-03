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
        self._io_expander0                  = None
        self._io_expander1                  = None
        self._leds                          = None
        self._buzzer                        = None
        self._eeprom                        = None
        self._flash                         = None
        self._ram                           = None
        self._rtc_communication             = None
        self._rtc_interrupt                 = None
        self._temperature_sensor_com        = None
        self._temperature_sensor_val        = None
        self._control_aliment_isol_plane    = None
        self._rs4850                        = None
        self._rs4851                        = None
        self._rs4852                        = None
        self._sdcard_insert                 = None
        self._sdcard_communication          = None
        self._ethernet_initizalization      = None
        self._ethernet_ping                 = None
        self._loopback                      = None
        self._details                       = None

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
    def io_expander0(self):
        return self._io_expander0

    @io_expander0.setter
    def io_expander0(self, value):
        self._io_expander0 = value

    @property
    def io_expander1(self):
        return self._io_expander1

    @io_expander1.setter
    def io_expander1(self, value):
        self._io_expander1 = value

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
    def temperature_sensor_com(self):
        return self._temperature_sensor_com

    @temperature_sensor_com.setter
    def temperature_sensor_com(self, value):
        self._temperature_sensor_com = value

    @property
    def temperature_sensor_val(self):
        return self._temperature_sensor_val

    @temperature_sensor_val.setter
    def temperature_sensor_val(self, value):
        self._temperature_sensor_val = value

    @property
    def control_aliment_isol_plane(self):
        return self._control_aliment_isol_plane

    @control_aliment_isol_plane.setter
    def control_aliment_isol_plane(self, value):
        self._control_aliment_isol_plane = value

    @property
    def rs4850(self):
        return self._rs4850

    @rs4850.setter
    def rs4850(self, value):
        self._rs4850 = value

    @property
    def rs4851(self):
        return self._rs4851

    @rs4851.setter
    def rs4851(self, value):
        self._rs4851 = value

    @property
    def rs4852(self):
        return self._rs4852

    @rs4852.setter
    def rs4852(self, value):
        self._rs4852 = value

    @property
    def sdcard_insert(self):
        return self._sdcard_insert

    @sdcard_insert.setter
    def sdcard_insert(self, value):
        self._sdcard_insert = value

    @property
    def sdcard_communication(self):
        return self._sdcard_communication

    @sdcard_communication.setter
    def sdcard_communication(self, value):
        self._sdcard_communication = value

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
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    def _get_udc_log_data(self):
        data = {}
        data['resultado_teste']                 = self._test_result
        data['numero_serie_udc']                = self._serial_number_udc
        data['io_expander0']                    = self._io_expander0
        data['io_expander1']                    = self._io_expander1
        data['leds']                            = self._leds
        data['buzzer']                          = self._buzzer
        data['eeprom']                          = self._eeprom
        data['flash']                           = self._flash
        data['ram']                             = self._ram
        data['rtc_communication']               = self._rtc_communication
        data['rtc_interrupt']                   = self._rtc_interrupt
        data['sensor_temperatura_com']          = self._temperature_sensor_com
        data['sensor_temperatura_val']          = self._temperature_sensor_val
        data['control_aliment_plano_isolado']   = self._control_aliment_isol_plane
        data['rs4850']                          = self._rs4850
        data['rs4851']                          = self._rs4851
        data['rs4852']                          = self._rs4852
        data['sdcard_inserido']                 = self._sdcard_insert
        data['sdcard_communication']            = self._sdcard_communication
        data['ethernet_inicializacao']          = self._ethernet_initizalization
        data['ethernet_ping']                   = self._ethernet_ping
        data['loopback']                        = self._loopback
        data['details']                         = self._details
        return data

    @property
    def data(self):
        return self._get_udc_log_data()

    @property
    def method(self):
        return "/AddLogUdc"

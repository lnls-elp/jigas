from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from common.elpwebclient import ElpWebClient
from common.pydrs import SerialDRS
from udcdata import UDC, UDCLog
import os, platform
import serial
import random
import time

class UDCTest(QThread):
    DISAPPROVED             = "Falha"
    APPROVED                = "OK"
    START_TEST              = 0x00
    READ_RESULT             = 0x01
    SUCESS                  = 0x00
    FAIL                    = 0x01
    SLEEP_TIME              = 0.05

    test_complete           = pyqtSignal(bool)
    update_gui              = pyqtSignal(str)
    connection_lost         = pyqtSignal()

    send_partial_complete   = pyqtSignal()

    buzzer_signal           = pyqtSignal(str)
    led_signal              = pyqtSignal(str)
    eeprom                  = pyqtSignal(str)
    flash                   = pyqtSignal(str)
    ram                     = pyqtSignal(str)
    adc                     = pyqtSignal(list)
    rtc                     = pyqtSignal(str)
    sensor_temp             = pyqtSignal(str)
    rs485                   = pyqtSignal(str)
    isol_plane              = pyqtSignal(str)
    io_expander             = pyqtSignal(str)
    ethernet_ping           = pyqtSignal(str)
    ethernet_init           = pyqtSignal(str)
    loopback                = pyqtSignal(str)

    def __init__(self, comport=None, baudrate=None, serial_number=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_number = serial_number
        self._led = None
        self._buzzer = None
        self._details = ""

        self._send_partial_data = False

        self._test_res_leds = False
        self._test_res_buzzer = False

        self._udc = SerialDRS()

    @property
    def send_partial_data(self):
        return self._send_partial_data

    @send_partial_data.setter
    def send_partial_data(self, value):
        self._send_partial_data = value

    @property
    def serial_number(self):
        return self._serial_number

    @serial_number.setter
    def serial_number(self, value):
        self._serial_number = value

    @property
    def led(self):
        return self._led

    @led.setter
    def led(self, value):
        self._led = value

    @property
    def buzzer(self):
        return self._buzzer

    @buzzer.setter
    def buzzer(self, value):
        self._buzzer = value

    @property
    def details(self):
        return self._details

    @details.setter
    def details(self, value):
        self._details = value

    @property
    def comport(self):
        return self._comport

    @comport.setter
    def comport(self, value):
        self._comport = value

    @property
    def baudrate(self):
        return self._baudarate

    @baudrate.setter
    def baudrate(self, value):
        self._baudrate = value

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            return self._udc.Connect(self._comport, self._baudrate)

    def test_communication(self):
        #result = False     # Result for communication test and aux power supply
        #try:
        #    self._udc.Write_sigGen_Aux(1)
        #    test_package = self._udc.Read_ps_Model()
        #    if (test_package[0] == 0) and (test_package[1] == 17) and (test_package[2] == 512) \
        #        and (test_package[3] == 14) and (test_package[4] == 223):
        #        result = True
        #except:
        #    pass
        result = True #Remove this
        return result

    def test_led(self):
        result = self.DISAPPROVED
        self.update_gui.emit("Testando Leds...")
        #self._udc.UdcLedTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcLedTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if (response is self.SUCESS):
            result = self.APPROVED
            self._test_res_led = True
        else:
            result = self.DISAPPROVED
            self._test_res_led = False
        self.led_signal.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def test_buzzer(self):
        self.update_gui.emit("Testando Buzzer...")
        result = self.DISAPPROVED
        #self._udc.UdcBuzzerTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcBuzzerTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if (response is self.SUCESS):
            result = self.APPROVED
            self._test_res_led = True
        else:
            result = self.DISAPPROVED
            self._test_res_led = False
        self.buzzer_signal.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_eeprom(self):
        self.update_gui.emit("Testando EEPROM...")
        serial_str = ""
        result = self.DISAPPROVED
        #self._udc.UdcEepromTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcEepromTest(self.READ_RESULT)
        """
            Simulate Value
        """
        #response = self._get_randon()
        response = [5, 9, 9 ,9, 5, 9, 9 ,9, 9, 9]
        """
            End Simulation
        """
        for item in response:
            serial_str += str(item)
        if serial_str is self._serial_number:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.eeprom.emit(result)
        self.update_gui.emit("Serial Lido: " + serial_str)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_flash(self):
        self.update_gui.emit("Testando Flash...")
        result = self.DISAPPROVED
        #self._udc.UdcFlashTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcFlashTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.flash.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_ram(self):
        self.update_gui.emit("Testando RAM...")
        result = self.DISAPPROVED
        #self._udc.UdcRamTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcRamTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.ram.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_adc(self):
        result = [self.DISAPPROVED for i in range(8)]
        result_bool = [False for i in range(8)]
        for i in range(1, 9):
            self.update_gui.emit("Testando ADC Canal " + str(i))
            #self._udc.UdcAdcTest(self.START_TEST, i)
            time.sleep(self.SLEEP_TIME)
            #response = self._udc.UdcAdcTest(self.READ_RESULT, i)
            """
                Simulate Value
            """
            response = self._get_randon()
            """
                End Simulation
            """
            if response is self.SUCESS:
                result[i - 1] = self.APPROVED
            else:
                result[i - 1] = self.DISAPPROVED
            self.update_gui.emit(result[i - 1])
        self.adc.emit(result)
        for i in range(8):
            if result[i] is self.APPROVED:
                result_bool[i] = True
        return result_bool

    def _test_rtc(self):
        self.update_gui.emit("Testando RTC...")
        result = self.DISAPPROVED
        #self._udc.UdcRtcTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcRtcTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.rtc.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_temperature_sensor(self):
        self.update_gui.emit("Testando Sensor de Temperatura...")
        result = self.DISAPPROVED
        #self._udc.UdcSensorTempTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcSensorTempTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.sensor_temp.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_rs485(self):
        self.update_gui.emit("Testando UART/RS485...")
        result = self.DISAPPROVED
        #self._udc.UdcUartTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcUartTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.rs485.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_alim_isol_plane(self):
        self.update_gui.emit("Testando Alimentação Plano Isolado...")
        result = self.DISAPPROVED
        #self._udc.UdcIsoPlaneTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcIsoPlaneTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.isol_plane.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_io_expander(self):
        self.update_gui.emit("Testando Expansor de I/O...")
        result = self.DISAPPROVED
        #self._udc.UdcIoExpanderTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcIoExpanderTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.io_expander.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_ethernet_init(self):
        self.update_gui.emit("Testando Inicialização Ethernet...")
        result = self.DISAPPROVED
        #self._udc.UdcEthernetTest(self.START_TEST)
        time.sleep(self.SLEEP_TIME)
        #response = self._udc.UdcEthernetTest(self.READ_RESULT)
        """
            Simulate Value
        """
        response = self._get_randon()
        """
            End Simulation
        """
        if response is self.SUCESS:
            result = self.APPROVED
        else:
            result = self.DISAPPROVED
        self.ethernet_init.emit(result)
        self.update_gui.emit(result)
        return (result is self.APPROVED)

    def _test_ethernet_ping(self):
        self.update_gui.emit("Testando Ping Ethernet...")
        host = "127.0.0.1"
        if  platform.system().lower()=="windows":
            ping_str = "-n 1"
        else:
            ping_str = "-c 1"
        resposta = os.system("ping " + ping_str + " " + host)
        if resposta is 0:
            self.ethernet_ping.emit(self.APPROVED)
            self.update_gui.emit(self.APPROVED)
            return True
        else:
            self.ethernet_ping.emit(self.DISAPPROVED)
            self.update_gui.emit(self.DISAPPROVED)
            return False

    def _test_periph_loopback(self):
        self.update_gui.emit("Testando Loopbacks...")
        result = self.DISAPPROVED
        result_bool = [False for i in range(32)]
        for i in range(1, 33):
            self.update_gui.emit("Testando Loopback canal " + str(i))
            #self._udc.UdcLoopBackTest(self.START_TEST, i)
            time.sleep(self.SLEEP_TIME)
            #response = self._udc.UdcLoopBackTest(self.READ_RESULT)
            """
                Simulate Value
            """
            response = self._get_randon()
            """
                End Simulation
            """
            if response is self.SUCESS:
                result_bool[i - 1] = True
                self.update_gui.emit(self.APPROVED)
            else:
                result_bool[i - 1] = False
                self._details += "\t Erro Loopback " + str(i)
                self.update_gui.emit(self.DISAPPROVED)
        if False in result_bool:
            result = self.DISAPPROVED
        else:
            result = self.APPROVED

        self.loopback.emit(result)
        return (result is self.APPROVED)

    def _test_sequence(self):
        result = False

        self.update_gui.emit("Iniciando Testes...")
        test_res_io_expander = self._test_io_expander()
        test_res_eeprom      = self._test_eeprom()
        test_res_flash       = self._test_flash()
        test_res_ram         = self._test_ram()
        test_res_rtc         = self._test_rtc()
        test_res_temp        = self._test_temperature_sensor()
        test_res_isol_plane  = self._test_alim_isol_plane()
        test_res_adc         = self._test_adc()
        test_res_uart        = self._test_rs485()
        test_res_loopback    = self._test_periph_loopback()
        test_res_ethern_init = self._test_ethernet_init()
        test_res_ethern_ping = self._test_ethernet_ping()

        udc = UDC()
        udc.serial_number = self._serial_number

        self.update_gui.emit("Cadastrando UDC no Servidor...")
        res = self._send_to_server(udc)

        if res:
            self.update_gui.emit("UDC Cadastrado com Sucesso!")

            log = UDCLog()
            log.serial_number_udc           = self._serial_number
            if test_res_io_expander:
                log.io_expander = self.APPROVED
            else:
                log.io_expander = self.DISAPPROVED

            if self._test_res_leds:
                log.leds = self.APPROVED
            else:
                log.leds = self.DISAPPROVED

            if self._test_res_buzzer:
                log.buzzer = self.APPROVED
            else:
                log.buzzer = self.DISAPPROVED

            if test_res_eeprom:
                log.eeprom = self.APPROVED
            else:
                log.eeprom = self.DISAPPROVED

            if test_res_flash:
                log.flash = self.APPROVED
            else:
                log.flash = self.DISAPPROVED

            if test_res_ram:
                log.ram = self.APPROVED
            else:
                log.ram = self.DISAPPROVED

            if test_res_rtc:
                log.rtc = self.APPROVED
            else:
                log.rtc = self.DISAPPROVED

            if test_res_uart:
                log.uart = self.APPROVED
            else:
                log.uart = self.DISAPPROVED

            if test_res_temp:
                log.temperature_sensor = self.APPROVED
            else:
                log.temperature_sensor = self.DISAPPROVED

            if test_res_isol_plane:
                log.control_aliment_isol_plane = self.APPROVED
            else:
                log.control_aliment_isol_plane = self.DISAPPROVED

            if test_res_ethern_init:
                log.ethernet_initialization = self.APPROVED
            else:
                log.ethernet_initialization = self.DISAPPROVED

            if test_res_ethern_ping:
                log.ethernet_ping = self.APPROVED
            else:
                log.ethernet_ping = self.DISAPPROVED

            if test_res_adc[0]:
                log.adc_ch_1 = self.APPROVED
            else:
                log.adc_ch_1 = self.DISAPPROVED

            if test_res_adc[1]:
                log.adc_ch_2 = self.APPROVED
            else:
                log.adc_ch_2 = self.DISAPPROVED

            if test_res_adc[2]:
                log.adc_ch_3 = self.APPROVED
            else:
                log.adc_ch_3 = self.DISAPPROVED

            if test_res_adc[3]:
                log.adc_ch_4 = self.APPROVED
            else:
                log.adc_ch_4 = self.DISAPPROVED

            if test_res_adc[4]:
                log.adc_ch_5 = self.APPROVED
            else:
                log.adc_ch_5 = self.DISAPPROVED

            if test_res_adc[5]:
                log.adc_ch_6 = self.APPROVED
            else:
                log.adc_ch_6 = self.DISAPPROVED

            if test_res_adc[6]:
                log.adc_ch_7 = self.APPROVED
            else:
                log.adc_ch_7 = self.DISAPPROVED

            if test_res_adc[7]:
                log.adc_ch_8 = self.APPROVED
            else:
                log.adc_ch_8 = self.DISAPPROVED

            if test_res_io_expander and self._led and self._buzzer and \
                test_res_eeprom and test_res_flash and test_res_ram and \
                test_res_rtc and test_res_temp and test_res_isol_plane and \
                test_res_adc and test_res_uart and test_res_loopback and \
                test_res_ethern_init and test_res_ethern_ping and \
                test_res_adc[0] and test_res_adc[1] and test_res_adc[2] and \
                test_res_adc[3] and test_res_adc[4] and test_res_adc[5] and \
                test_res_adc[6] and test_res_adc[7]:
                log.test_result = 'Aprovado'
                result = True
            else:
                log.test_result = 'Reprovado'
                result = False

            self.update_gui.emit("Enviando dados de teste...")
            server_response = self._send_to_server(log)
            if server_response:
                self.update_gui.emit("Dados Enviados com Sucesso!")
            else:
                self.update_gui.emit("Erro ao enviar dados")
            self.test_complete.emit(result)

        else:
            self.update_gui.emit("Erro ao Cadastrar UDC no servidor!")

    def _send_partial(self):
        udc = UDC()
        udc.serial_number = self._serial_number
        log = UDCLog()
        log.serial_number_udc = self._serial_number
        log.test_result = 'Reprovado'
        log.details = self._details
        res = self._send_to_server(udc)
        if res:
            self._send_to_server(log)
        self.send_partial_complete.emit()

    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        print("***** RESPOSTA ******")
        print()
        print(client_response)
        print()
        server_status = self._parse_response(client_response)
        return server_status

    def _parse_response(self, response):
        res_key = 'StatusCode'
        err_key = 'error'

        if res_key in response.keys() and err_key not in response.keys():
            return True
        else:
            return False

    """
        Test function
    """
    def _get_randon(self):
        return random.randint(0,1)

    def _get_pass(self):
        return self.SUCCESS

    def run(self):
        if self._send_partial_data:
            self._send_partial()
        else:
            self._test_sequence()
        #pass

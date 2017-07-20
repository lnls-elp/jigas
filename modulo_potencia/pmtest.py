from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from pmdata import *
import serial

class PowerModuleTest(QThread):
    test_complete       = pyqtSignal(list)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None,
                    mod0=None, mod1=None, mod2=None, mod3=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_mod0 = mod0
        self._serial_mod1 = mod1
        self._serial_mod2 = mod2
        self._serial_mod3 = mod3
        self._serial_port = serial.Serial()

        # 4 Power Module objets (emit when test finished)
        self._log = [None for i in range(4)]

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

    @property
    def serial_mod0(self):
        return self._serial_mod0

    @serial_mod0.setter
    def serial_mod0(self, value):
        self._serial_mod0 = value

    @property
    def serial_mod1(self):
        return self._serial_mod1

    @serial_mod1.setter
    def serial_mod1(self, value):
        self._serial_mod1 = value

    @property
    def serial_mod2(self):
        return self._serial_mod2

    @serial_mod2.setter
    def serial_mod2(self, value):
        self._serial_mod2 = value

    @property
    def serial_mod3(self):
        return self._serial_mod3

    @serial_mod3.setter
    def serial_mod3(self, value):
        self._serial_mod3 = value

    def open_serial_port(self):
        if self._comport is None or self._baudrate is None:
            return False
        else:
            self._serial_port.baudrate  = self._baudrate
            self._serial_port.port      = self._comport
            self._serial_port.open()
            return self._serial_port.is_open

    def test_communication(self):
        # Resultado teste de comunicação para os 4 módulos
        result = [None for i in range(4)]
        #TODO: Communication test
        return result

    def _test_sequence(self):
        serial = [self._serial_mod0, self._serial_mod1, self._serial_mod2,
                    self._serial_mod3]

        if not self._serial_port.is_open:
            self.connection_lost.emit()
            return

        for item in serial:
            if item is not None:
                pmlog = PowerModuleLog()
                pmlog.serial_number_power_module = item

                # TODO: Faz os testes e seta os atributos de log

                #salva na lista de logs para retornar
                self._log[serial.indexOf(item)]
        # Quando o teste terminar emitir o resultado em uma lista de objetos
        # do tipo PowerModuleLog
        self.test_complete.emit(self._log)

    def run(self):
        #self._test_sequence()
        pass

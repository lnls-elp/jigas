from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import serial

class RackTest(QThread):
    test_complete       = pyqtSignal(dict)
    connection_lost     = pyqtSignal()

    def __init__(self, comport=None, baudrate=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_port = serial.Serial()

        self._test_result = {}
        self._test_result['result']     = ""
        self._test_result['iout']       = []
        self._test_result['details']    = ""

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
            self._serial_port.baudrate  = self._baudrate
            self._serial_port.port      = self._comport
            self._serial_port.open()
            return self._serial_port.is_open

    def test_communication(self):
        result = False     # Result for communication test
        #TODO: Communication test
        return result

    def _test_sequence(self):
        # If serial connection is lost
        if not self._serial_port.is_open:
            self.connection_lost.emit()
        #TODO: Sequencia de Testes
        # ao finalizar, emitir signals
        self.test_complete.emit(self._test_result)

    def run(self):
        #TODO: All
        pass

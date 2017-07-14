from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import serial

class DCCTTest(QThread):
    test_complete = pyqtSignal(dict)

    def __init__(self, comport=None, baudrate=None):
        QThread.__init__(self)
        self._comport = comport
        self._baudarate = baudrate
        self._serial_port = serial.Serial()

        self._load_current = [0, 2, 4, 6, 8, 10, -10, -8, -6, -4, -2]
        self._test_result = {}
        self._test_result['result'] = ""
        self._test_result['iload']  = []

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

    def _test_sequence(self):
        #TODO: Sequencia de Testes
        # ao finalizar, emitir signals


    def run(self):
        #TODO: All
        pass

#!/usr/bin/python3
import sys
from PyQt5 import uic
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QWizard, QApplication

class DCCTWindow(QWizard):

    def __init__(self, parent=None):
        super(DCCTWindow, self).__init__(parent)
        uic.loadUi('wizard.ui', self)

        self._SERIAL_BAUDRATE = 115200

        self._initialize_widgets()
        self._initialize_signals()

    @pyqtSlot()
    def _read_serial_number(self):
        #TODO: Read serial number routine
        print("Read Serial Number")

    @pyqtSlot()
    def _treat_read_serial_edit(self):
        if self.cbEnableSerialNumberEdit.isChecked():
            self.leSerialNumber.setReadOnly(False)
        else:
            self.leSerialNumber.setReadOnly(True)

    @pyqtSlot()
    def _connect_serial_port(self):
        #TODO: Connect and test serial port
        pass

    @pyqtSlot()
    def _start_test_sequence(self):
        #TODO: Start test sequence thread
        pass

    @pyqtSlot()
    def _submit_test_report(self):
        #TODO: Submit report to server
        pass

    def _initialize_widgets(self):
        """ Initial widgets configuration """
        self.leBaudrate.setText(str(self._SERIAL_BAUDRATE))
        self.leBaudrate.setReadOnly(True)
        self.leSerialNumber.setReadOnly(True)

    def _initialize_signals(self):
        """ Configure basic signals """
        self.pbReadSerialNumber.clicked.connect(self._read_serial_number)
        self.cbEnableSerialNumberEdit.stateChanged.connect(self._treat_read_serial_edit)
        self.pbConnectSerialPort.clicked.connect(self._connect_serial_port)
        self.pbStartTests.clicked.connect(self._start_test_sequence)
        self.pbSubmitTestReport.clicked.connect(self._submit_test_report)


#app = QApplication(sys.argv)
#GUI = Window()
#GUI.show()
#sys.exit(app.exec_())
if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = DCCTWindow()
    gui.show()
    sys.exit(app.exec_())

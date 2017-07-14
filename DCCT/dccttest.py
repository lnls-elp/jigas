from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal

class DCCTTest(QThread):
    test_complete = pyqtSignal(dict)

    def __init__(self):
        QThread.__init__(self)
        #TODO: All
        pass

    def run(self):
        #TODO: All
        pass

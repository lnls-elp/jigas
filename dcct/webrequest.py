from PyQt5.QtCore import QThread, pyqtSignal
import simplejson as json
from elpwebclient import *
import time


class WebRequest(QThread):

    server_response = pyqtSignal(dict, dict)

    def __init__(self, device=None, log=None):
        QThread.__init__(self)
        self._device = device
        self._log = log

    @property
    def device(self):
        return self._device

    @device.setter
    def device(self, value):
        self._device = value

    @property
    def log(self):
        return self._log

    @log.setter
    def log(self, value):
        self._log = value

    def _create_request(self):
        device_client = ElpWebClient()
        device_data = self._device.data
        device_method = self._device.method
        device_res = device_client.do_request(device_method, device_data)

        log_client = ElpWebClient()
        log_data = self._log.data
        log_method = self._log.method
        log_res = log_client.do_request(log_method, log_data)

        self.server_response.emit(device_res, log_res)

    def run(self):
        self._create_request()

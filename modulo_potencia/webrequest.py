from PyQt5.QtCore import QThread, pyqtSignal
import simplejson as json
from elpwebclient import *
from pmdata import *
import time


class WebRequest(QThread):

    server_response = pyqtSignal(list)

    (ret_success, ret_error) = ('Success', 'Fail')

    res_key = 'StatusCode'
    err_key = 'error'


    def __init__(self, log_data=[]):
        QThread.__init__(self)
        self._log_data = log_data
        self._result = [None for i in range(4)]

    @property
    def log_data(self):
        return self._log_data

    @log_data.setter
    def log_data(self, value):
        self._log_data = value


    def _create_request(self):
        for item in self._log_data:
            if item is not None:
                #Create request for device first
                device = PowerModule(item.serial_number_power_module)
                device_client = ElpWebClient()
                device_data = device.data
                device_method = device.method
                device_res = device_client.do_request(device_method, device_data)

                if res_key in device_res.keys():
                    #Create request for log
                    log_client = ElpWebClient()
                    log_data = item.data
                    log_method = item.method
                    log_res = log_client.do_request(log_method, log_data)
                    if res_key in log_res.keys():
                        self._result[self._log_data.index(item)] = ret_success
                    elif err_key in log_res.keys():
                        self._result[self._log_data.index(item)] = ret_error
                    else:
                        self._result[self._log_data.index(item)] = log_res
                else:
                    self._result[self._log_data.index(item)] = ret_error
            else:
                self._result[self._log_data.index(item)] = None

        self.server_response.emit(self._result)

    def run(self):
        self._create_request()

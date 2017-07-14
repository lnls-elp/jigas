from PyQt5.QtCore import QThread, pyqtSignal
import simplejson as json
from elpwebclient import *
import time


class WebRequest(QThread):

    server_response = pyqtSignal(dict)

    def __init__(self, method=None, data={}):
        QThread.__init__(self)
        self._method = method
        self._data = data

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, value):
        self._method = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    def _create_request(self):
        client = ElpWebClient()
        data = self._data
        method = self._method
        res = client.do_request(method, data)
        res_dict - json.loads(res)
        self.server_response.emit(res_dict)

    def run(self):
        self._create_request()

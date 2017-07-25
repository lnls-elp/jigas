from PyQt5.QtCore import QThread, pyqtSignal
import simplejson as json
from elpwebclient import *
from dcctdata import *

class WebRequest(QThread):

    server_response = pyqtSignal(list)

    def __init__(self, items = []):
        QThread.__init__(self)
        self._items = items
        self._response = []

    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, value):
        self._items = value

    def _create_request(self):
        for item in self._items:
            if item is not None:
                client = ElpWebClient()
                client_data = item.data
                client_method = item.method
                client_response = client.do_request(client_method, client_data)
                result = self._parse_response(client_response)
                self._response.append(result)
            else:
                self._response.append(None)

        self.server_response.emit(self._response)

    def _parse_response(self, response):
        res_key = 'StatusCode'
        err_key = 'error'

        if res_key in response.keys() and err_key not in response.keys():
            return True
        else:
            return False

    def run(self):
        self._create_request()

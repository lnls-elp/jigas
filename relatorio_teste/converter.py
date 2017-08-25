from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
import requests


class Converter(QThread):
    conversion_complete = pyqtSignal(bool)

    def __init__(self, comport=None, baudrate=None, serial_number=None, variant=None):
        QThread.__init__(self)
        self._url = 'http://186.249.222.195'


    def _get_json(self):


    def _send_to_server(self, item):
        client = ElpWebClient()
        client_data = item.data
        client_method = item.method
        client_response = client.do_request(client_method, client_data)
        print(client_response)
        server_status = self._parse_response(client_response)
        return server_status

    def _parse_response(self, response):
        res_key = 'StatusCode'
        err_key = 'error'

        if res_key in response.keys() and err_key not in response.keys():
            return True
        else:
            return False

    def run(self):
        self._test_sequence()
        #pass

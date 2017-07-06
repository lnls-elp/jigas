from elpwebclient import *
import simplejson as json

class DCCTData:

    def __init__(self, serial_number):
        self._serial_number = serial_number
        self._device_type = "DCCT"

    def _get_device_data(self):
        data = {}
        data['serial_number'] = self._serial_number
        data['type'] = self._device_type
        return data

    def add_device(self):
        client = ElpWebClient()
        data = self._get_device_data()
        method = "/AddDevice"
        response = client.do_request(method, data)
        return response


teste = DCCTData(546, "UHD")

print(teste.add_device())

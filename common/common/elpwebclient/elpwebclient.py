import requests

class ElpWebClient:
    def __init__(self, url='http://10.0.0.120:80'):
        self._url = url

    """
    Send Data to Web server
    method: string with method name for web api. Ex: '/AddDevice'
    parameters: dictionary with data to create json request
    """
    def do_request(self, method, parameters):
        complete_url = self._url + method
        data = parameters
        response = requests.post(complete_url, data)
        return response.json()

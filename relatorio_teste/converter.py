from PyQt5.QtCore import pyqtSlot, QThread, pyqtSignal
from datetime import datetime
import numpy as np
import requests
import csv


class Converter(QThread):
    conversion_complete = pyqtSignal(bool)

    def __init__(self, resource='/'):
        QThread.__init__(self)
        self._url = 'http://186.249.222.195'
        self._resource = resource

    @property
    def resource(self):
        return self._resource

    @resource.setter
    def resource(self, value):
        self._resource = value

    def _get_json(self):
        try:
            report_url = self._url + self._resource
            res = requests.get(report_url)
            array = np.array(res.json())
            return array
        except Exception as e:
            return "Erro: " + str(e)

    def _get_header(self):
        res = self._resource
        if res == '/HradcReport':
            header = ['Data', 'Serial', 'Variante', 'Medida', 'GND',
                    'Vref Pos', 'Vref Neg', 'Temperatura',
                    'Vin Pos', 'Vin Neg', 'Iin Pos', 'Iin Neg',
                    'Resultado', 'Detalhes']
            return header

        elif res == '/HradcCalibReport':
            header = ['Data', 'Serial', 'Operador', 'Variante',
                    'Temperatura HRADC', 'Temperatura DMM',
                    'Temperatura Fonte', 'Ganho Vin', 'Offset Vin',
                    'Ganho Iin', 'Offset Iin', 'Vref Pos', 'Vref Neg',
                    'GND']
            return header

        elif res == '/DcctReport':
            header = ['Data', 'Serial', 'Variante', 'Canal', 'On/Off',
                    'iLoad 0', 'iLoad 1', 'iLoad 2', 'iLoad 3', 'iLoad 4',
                    'iLoad 5', 'iLoad 6', 'iLoad 7', 'iLoad 8', 'iLoad 9',
                    'iLoad 10', 'Resultado']
            return header

        elif res == '/PowerModuleReport':
            header = ['Data', 'Serial',
                    'iLoad 0', 'iLoad 1', 'iLoad 2', 'iLoad 3', 'iLoad 4', 'iLoad 5',
                    'vLoad 0', 'vLoad 1', 'vLoad 2', 'vLoad 3', 'vLoad 4', 'vLoad 5',
                    'vdclink 0', 'vdclink 1', 'vdclink 2', 'vdclink 3', 'vdclink 4', 'vdclink 5',
                    'Temperatura 0', 'Temperatura 1', 'Temperatura 2', 'Temperatura 3', 'Temperatura 4', 'Temperatura 5',
                    'Resultado', 'Detalhes']
            return header

        elif res == '/PowerSupplyReport':
            header = ['Data', 'Serial', 'Canal', 'Teste',
                    'On/Off', '+20 Duty Cycle', '-20 Duty Cycle', 'iout 0', 'iout 1',
                    'vout 0', 'vout 1', 'vdclink 0', 'vdclink 1', 'Temperatura 0', 'Temperatura 1',
                    'Resultado', 'Detalhes']
            return header

        elif res == '/RackReport':
            header = ['Data', 'Serial',
                    'iout 0', 'iout 1', 'iout 2', 'iout 3',
                    'delta iout 0', ' delta iout 1',
                    'delta iout 2', 'delta iout 3',
                    'Resultado', 'Detalhes']
            return header

        elif res == '/UdcReport':
            header = ['Data', 'Resultado', 'Serial', 'Leds', 'Buzzer', 'EEPROM',
                    'FLASH', 'RAM', 'Alimentação Plano Isolado', 'Ethernet Ping',
                    'Loopback', 'Expansor I/O', 'RTC', 'Sensor Temperatura', 'RS485',
                    'ADC 1', 'ADC 2', 'ADC 3', 'ADC 4', 'ADC 5', 'ADC 6', 'ADC 7',
                    'ADC 8','Detalhes',]
            return header

        return []

    def _generate_csv(self):
        res = self._get_json()
        if not (len(res) > 0):
            self.conversion_complete.emit(False)
        else:
            now = datetime.now()
            now_str = str(now.day) + "_" + str(now.month) + "_" + str(now.day) + "_" + \
                        str(now.hour) + "_" + str(now.minute) + "_" + str(now.second)
            nome_begin = self.resource[1:]
            nome = nome_begin + now_str + '.csv'
            path = './relatorios/' + nome
            f = open(path, 'wt')
            try:
                writer = csv.writer(f)
                writer.writerow(self._get_header())
                writer.writerows(res)
            finally:
                f.close()
            self.conversion_complete.emit(True)

    def run(self):
        self._generate_csv()

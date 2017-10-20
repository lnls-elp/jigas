from PyQt5.QtWidgets import QWidget

class Scanner(QWidget):

    materiais = {'14024288': 'POT-FBP-SLOW',
                '14024289': 'HRADC-FBP',
                '14024290': 'HRADC-FAX',
                '14024291': 'UDC-FBP',
                '14024292': 'DCCT-CONF-A',
                '14024295': 'DCCT-CONF-B',
                '14026758': 'Bastidor',
                '14019820': 'FBP 4 CH LP'
                '14019821': 'FBP 4 CH'
                '14019821': 'FBP 4 CH',
                '14019822': 'FBP 3 CH',
                '14019823': 'FBP 2 CH'}

    def parse_code(self, code):
        data = {}
        if code is not None and code is not "":
            code = code.split(" ")
            try:
                #data['material'] = code[0]
                #data['var1']     = code[1]
                #data['var2']     = code[2]
                #data['serial']   = code[1][2:]
                data['serial']   = code[0][2:]
                data['material'] = code[1][3:]
                return data
            except IndexError:
                return None
        return None

    def get_material_name(self, material_code):
        if material_code in self.materiais.keys():
            return self.materiais[material_code]
        return "NAO EXISTE"

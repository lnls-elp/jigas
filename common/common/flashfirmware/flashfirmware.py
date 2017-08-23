import subprocess

class LoadFirmware:

    def __init__(self, arm_pathtofile=None, c28_pathtofile=None):

        self._arm = arm_pathtofile
        self._c28 = c28_pathtofile
        self.status = "initialized"

    @property
    def arm_pathtofile(self):
        return self._arm

    @arm_pathtofile.setter
    def arm_pathtofile(self, path):
        self._arm = path

    @property
    def c28_pathtofile(self):
        return self._c28

    @c28_pathtofile.setter
    def c28_pathtofile(self, path):
        self._c28 = path

    def flash_firmware(self, core):
        print("flashing firmware...")
        if core == 'arm':
            flashcommand = " CMD /C ccs_base\\DebugServer\\bin\\DSLite flash -c user_files/configs/f28m36p63c2.ccxml -l user_files/settings/generated.ufsettings  -f -v " + self._arm
        if core == 'c28':
            flashcommand = " CMD /C ccs_base\\DebugServer\\bin\\DSLite flash -c user_files/configs/f28m36p63c2.ccxml -l user_files/settings/generated.ufsettings --core=1 -f -v " + self._c28

        proc = subprocess.Popen(flashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        if err:
            print("ERRO")
            out = out.decode("utf-8")
            err = err.decode("utf-8")
            print("out:   " + out)
            print("err:   "+err)
            if "problem loading file" in err:
                if "Could not open file" in err:
                    print("arquivo nao encontrado")
                    self.status = "file not found fault"
                elif "Could not determine target type of file" in err:
                    print("arquivo incompativel ou corrompido")
                    self.status = "file extension fault"
                else:
                    print("erro com o arquivo.")
                    self.status = "file unknown error"
            elif "Operation was aborted" in err:
                if "FTDI driver" in out:
                    print("cabo desconectado")
                    self.status = "cable fault"
                elif "power loss" in out:
                    print("problema de alimentacao")
                    self.status = "power fault"
                else:
                    print("problema desconhecido")
                    self.status = "aborted unknown error"
            elif "Does not match the target type" in err:
                self.status = "target file error"
            elif "nothing to do" in err:
                self.status = "missing file error"
            else:
                self.status = "unknown error"
        else:
            self.status = "success"
            print("OK")
        return(self.status)

    def log_status(self):
        if self.status == "success":
            return("código gravado com sucesso!")

        elif self.status == "file not found fault":
            return "erro : arquivo não encontrado."

        elif self.status == "file extension fault":
            return "erro : arquivo não é do tipo esperado ou está corrompido."

        elif self.status == "file unknown error":
            return "erro : não foi possível abrir o arquivo escolhido."

        elif self.status == "cable fault":
            return "erro : o computador não detectou a conexão USB com o gravador."

        elif self.status == "power fault":
            return "erro : o dispositivo não está ligado."

        elif self.status == "aborted unknown error":
            return "erro : gravação interrompida."

        elif self.status == "target file error":
            return "erro : o arquivo selecionado não corresponde ao núcleo."

        elif self.status == "unknown error":
            return "erro desconhecido."

        elif self.status == "initialized":
            return "nenhuma tentativa de gravação realizada."

        else:
            return "."

class LoadFirmware_HRADC:
    
    def __init__(self, pathtofile='..\\common\\common\\flashfirmware\\hradc_cpld_files\\HRADC_v2_1_CPLD_Firmware.cdf'):

        self._path = pathtofile
        self.status = "initialized"

    @property
    def pathtofile(self):
        return self._path

    @pathtofile.setter
    def pathtofile(self, path):
        self._path = path

    def load_firmware(self):
        print("flashing firmware...")
        command = " CMD /C c:\\altera\\16.0\\qprogrammer\\bin64\\quartus_pgm --quiet -c USB-Blaster " + self._path
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.decode("utf-8")
        #print("out:   " + out)

        if "Successfully performed operation" in out:
            self.status = "Firmware gravado com sucesso"

        elif "Programming hardware cable not detected" in out:
            self.status = "Erro: Gravador USB-Blaster nao encontrado"
                
        elif "Can't access JTAG chain" in out:
            self.status = "Erro: CPLD nao encontrada"

        elif "Error (210007): Can't locate programming file" in out:
            self.status = "Erro: Arquivo binario POF nao encontrado"

        elif "Error (213009): File name" in out:
            self.status = "Erro: Arquivo de configuracao CDF nao encontrado"

        else:
            self.status = "Erro desconhecido"

        print(self.status)
        return(self.status)
    '''
    def log_status(self):
        if self.status == "success":
            return("codigo gravado com sucesso!")

        elif self.status == "usb-blaster not found":
            return "erro : o computador nao detectou a conexao USB com o gravador"

        elif self.status == "cpld not found":
            return "erro : o gravador nao detectou a CPLD"

        elif self.status == "pof file not found":
            return "erro : arquivo binario POF nao encontrado."

        elif self.status == "cdf file not found":
            return "erro : arquivo de configuracao CDF nao encontrado"
        
        elif self.status == "unknown error":
            return "erro desconhecido."

        elif self.status == "initialized":
            return "nenhuma tentativa de gravação realizada."

        else:
            return "."
        '''

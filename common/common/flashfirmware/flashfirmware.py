import subprocess

class LoadFirmware:

    def __init__(self, arm_pathtofile=None, c28_pathtofile=None):

        self._arm = arm_pathtofile
        self._c28 = c28_pathtofile

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
            print("ERRO AO GRAVAR FIRMWARE")
            out = out.decode("utf-8")
            errormessage = out.find("(Error")
            if errormessage:
                errorcode = out[errormessage+8:errormessage+11]
                print(errorcode)
                if errorcode == "151":
                    print ("CABO DESCONECTADO")
                elif errorcode == "180":
                    print ("PROBLEMA DE ALIMENTACAO")
                return(int(errorcode))
        else:
            print("FIRMWARE GRAVADO COM SUCESSO")
            return(0)
        

from PyQt5.QtCore import pyqtSignal, QThread
import subprocess
import os

class LoadFirmware(QThread):

    ARM_COMMAND = " CMD /C ..\\common\\common\\flashfirmware\\ccs_base\\DebugServer\\bin\\DSLite flash -c ../common/common/flashfirmware/user_files/configs/f28m36p63c2.ccxml -l user_files/settings/generated.ufsettings  -f -v "
    C28_COMMAND = " CMD /C ..\\common\\common\\flashfirmware\\ccs_base\\DebugServer\\bin\\DSLite flash -c ../common/common/flashfirmware/user_files/configs/f28m36p63c2.ccxml -l user_files/settings/generated.ufsettings --core=1 -f -v "

    ARM_TEST_FWR = '..\\common\\common\\flashfirmware\\udc_firmware\\test\\arm_test.out'
    C28_TEST_FWR = '..\\common\\common\\flashfirmware\\udc_firmware\\test\\dsp_test.out'

    ARM_FINAL_FWR = '..\\common\\common\\flashfirmware\\udc_firmware\\final\\arm_final.out'
    C28_FINAL_FWR = '..\\common\\common\\flashfirmware\\udc_firmware\\final\\dsp_final.out'

    load_test_finished       = pyqtSignal(bool)
    update_test_firmware_log  = pyqtSignal(str)

    load_final_finished      = pyqtSignal(bool)
    update_final_firmware_log = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)
        self._status = False
        self._is_final = False

    @property
    def load_final(self):
        return self._is_final

    @load_final.setter
    def load_final(self, value):
        self._is_final = value

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, value):
        self._status = value

    def _load_final_firmware(self):
        self._status = False
        arm_result = ""
        c28_result = ""

        self.update_final_firmware_log.emit("Gravando Firmware Final")

        """
            Loading ARM
        """
        self.update_final_firmware_log.emit("Gravando Núcleo ARM...")
        flashcommand = self.ARM_COMMAND + self.ARM_FINAL_FWR
        proc = subprocess.Popen(flashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        if err:
            self.update_final_firmware_log.emit("Erro!")
            out = out.decode("ISO-8859-1")
            err = err.decode("ISO-8859-1")
            self.update_final_firmware_log.emit("out: " + out)
            self.update_final_firmware_log.emit("err: " + err)
            if "problem loading file" in err:
                if "Could not open file" in err:
                    self.update_final_firmware_log.emit("Arquivo Não Encontrado")
                    arm_result = "file not found fault"
                elif "Could not determine target type of file" in err:
                    self.update_final_firmware_log.emit("Arquivo Incompatível ou Corrompido")
                    arm_result = "file extension fault"
                else:
                    self.update_final_firmware_log.emit("Erro com o arquivo.")
                    arm_result = "file unknown error"
            elif "Operation was aborted" in err:
                if "FTDI driver" in out:
                    self.update_final_firmware_log.emit("Cabo desconectado")
                    arm_result = "cable fault"
                elif "power loss" in out:
                    self.update_final_firmware_log.emit("Problema de Alimentação")
                    arm_result = "power fault"
                else:
                    self.update_final_firmware_log.emit("Problema desconhecido")
                    arm_result = "aborted unknown error"
            elif "Does not match the target type" in err:
                arm_result = "target file error"
            elif "nothing to do" in err:
                arm_result = "missing file error"
            else:
                arm_result = "unknown error"
        else:
            arm_result = "success"
            self.update_final_firmware_log.emit("ARM gravado com Sucesso!")
        """
            Loading C28
        """
        self.update_final_firmware_log.emit("Gravando Núcleo C28...")
        flashcommand = self.C28_COMMAND + self.C28_TEST_FWR
        proc = subprocess.Popen(flashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        if err:
            self.update_final_firmware_log.emit("Erro!")
            out = out.decode("ISO-8859-1")
            err = err.decode("ISO-8859-1")
            self.update_final_firmware_log.emit("out: " + out)
            self.update_final_firmware_log.emit("err: " + err)
            if "problem loading file" in err:
                if "Could not open file" in err:
                    self.update_final_firmware_log.emit("Arquivo Não Encontrado")
                    c28_result = "file not found fault"
                elif "Could not determine target type of file" in err:
                    self.update_final_firmware_log.emit("Arquivo Incompatível ou Corrompido")
                    c28_result = "file extension fault"
                else:
                    self.update_final_firmware_log.emit("Erro com o arquivo.")
                    c28_result = "file unknown error"
            elif "Operation was aborted" in err:
                if "FTDI driver" in out:
                    self.update_final_firmware_log.emit("Cabo desconectado")
                    c28_result = "cable fault"
                elif "power loss" in out:
                    self.update_final_firmware_log.emit("Problema de Alimentação")
                    c28_result = "power fault"
                else:
                    self.update_final_firmware_log.emit("Problema desconhecido")
                    c28_result = "aborted unknown error"
            elif "Does not match the target type" in err:
                c28_result = "target file error"
            elif "nothing to do" in err:
                c28_result = "missing file error"
            else:
                c28_result = "unknown error"
        else:
            c28_result = "success"
            self.update_final_firmware_log.emit("C28 gravado com Sucesso!")

        if arm_result is 'success' and c28_result is 'success':
            self._status = True
        else:
            self._status = False

        self.load_final_finished.emit(self._status)

    def _load_test_firmware(self):
        self._status = False
        arm_result = ""
        c28_result = ""

        self.update_test_firmware_log.emit("Gravando Firmware de Teste")

        """
            Loading ARM
        """
        self.update_test_firmware_log.emit("Gravando Núcleo ARM...")
        flashcommand = self.ARM_COMMAND + self.ARM_TEST_FWR
        proc = subprocess.Popen(flashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        if err:
            self.update_test_firmware_log.emit("Erro!")
            out = out.decode("ISO-8859-1")
            err = err.decode("ISO-8859-1")
            self.update_test_firmware_log.emit("out: " + out)
            self.update_test_firmware_log.emit("err: " + err)
            if "problem loading file" in err:
                if "Could not open file" in err:
                    self.update_test_firmware_log.emit("Arquivo Não Encontrado")
                    arm_result = "file not found fault"
                elif "Could not determine target type of file" in err:
                    self.update_test_firmware_log.emit("Arquivo Incompatível ou Corrompido")
                    arm_result = "file extension fault"
                else:
                    self.update_test_firmware_log.emit("Erro com o arquivo.")
                    arm_result = "file unknown error"
            elif "Operation was aborted" in err:
                if "FTDI driver" in out:
                    self.update_test_firmware_log.emit("Cabo desconectado")
                    arm_result = "cable fault"
                elif "power loss" in out:
                    self.update_test_firmware_log.emit("Problema de Alimentação")
                    arm_result = "power fault"
                else:
                    self.update_test_firmware_log.emit("Problema desconhecido")
                    arm_result = "aborted unknown error"
            elif "Does not match the target type" in err:
                arm_result = "target file error"
            elif "nothing to do" in err:
                arm_result = "missing file error"
            else:
                arm_result = "unknown error"
        else:
            arm_result = "success"
            self.update_test_firmware_log.emit("ARM gravado com Sucesso!")
        """
            Loading C28
        """
        self.update_test_firmware_log.emit("Gravando Núcleo C28...")
        flashcommand = self.C28_COMMAND + self.C28_TEST_FWR
        proc = subprocess.Popen(flashcommand.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

        if err:
            self.update_test_firmware_log.emit("Erro!")
            out = out.decode("ISO-8859-1")
            err = err.decode("ISO-8859-1")
            self.update_test_firmware_log.emit("out: " + out)
            self.update_test_firmware_log.emit("err: " + err)
            if "problem loading file" in err:
                if "Could not open file" in err:
                    self.update_test_firmware_log.emit("Arquivo Não Encontrado")
                    c28_result = "file not found fault"
                elif "Could not determine target type of file" in err:
                    self.update_test_firmware_log.emit("Arquivo Incompatível ou Corrompido")
                    c28_result = "file extension fault"
                else:
                    self.update_test_firmware_log.emit("Erro com o arquivo.")
                    c28_result = "file unknown error"
            elif "Operation was aborted" in err:
                if "FTDI driver" in out:
                    self.update_test_firmware_log.emit("Cabo desconectado")
                    c28_result = "cable fault"
                elif "power loss" in out:
                    self.update_test_firmware_log.emit("Problema de Alimentação")
                    c28_result = "power fault"
                else:
                    self.update_test_firmware_log.emit("Problema desconhecido")
                    c28_result = "aborted unknown error"
            elif "Does not match the target type" in err:
                c28_result = "target file error"
            elif "nothing to do" in err:
                c28_result = "missing file error"
            else:
                c28_result = "unknown error"
        else:
            c28_result = "success"
            self.update_test_firmware_log.emit("C28 gravado com Sucesso!")

        if arm_result is 'success' and c28_result is 'success':
            self._status = True
        else:
            self._status = False

        self.load_test_finished.emit(self._status)


    def run(self):
        if self._is_final:
            self._load_final_firmware()
        else:
            self._load_test_firmware()

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
        print("\nGravando firmware...")

        #command = " CMD /C c:\\altera\\16.0\\qprogrammer\\bin64\\quartus_pgm -c USB-Blaster " + self._path
        #command = " CMD /C c:\\intelFPGA\\16.1\\qprogrammer\\bin64\\quartus_pgm -c USB-Blaster " + self._path
        command = " CMD /C c:\\intelFPGA_lite\\17.0\\quartus\\bin64\\quartus_pgm -c USB-Blaster " + self._path
        proc = subprocess.Popen(command.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (out, err) = proc.communicate()
        out = out.decode("utf-8")
        #print("out:   " + out)

        #out = "Successfully performed operation"

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

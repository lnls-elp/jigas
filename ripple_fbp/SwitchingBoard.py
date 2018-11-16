##
#programa switchingBoard_FBP
#Paulo Ricardo
##

#define bibliotecas IO.
import RPi.GPIO as GPIO

#Define biblioteca de tempo em segundos
import time         
GPIO.setmode(GPIO.BCM)

#Setar Pinos como Saida
GPIO.setup(3, GPIO.OUT)     #Rele 1
GPIO.setup(4, GPIO.OUT)     #Rele 2
GPIO.setup(17, GPIO.OUT)    #Rele 3
GPIO.setup(27, GPIO.OUT)    #Rele 4

GPIO.output(3,0)
GPIO.output(4,0)
GPIO.output(17,0)
GPIO.output(27,0)



def switchingBoard_FBP(rele):
    if rele == 1:
        # print ("\tCarga OFF: 1 \n\tCargas ON: 2,3,4 e TestLoad")
        GPIO.output(3,1)
        GPIO.output(4,0)
        GPIO.output(17,0)
        GPIO.output(27,0)
        
    elif rele == 2:
        # print ("\tCarga OFF: 2 \n\tCargas ON: 1,3,4 e TestLoad")
        GPIO.output(3,0)
        GPIO.output(4,1)
        GPIO.output(17,0)
        GPIO.output(27,0)
        
    elif rele == 3:
        # print ("\tCarga OFF: 3 \n\tCargas ON: 1,2,4 e TestLoad")
        GPIO.output(3,0)
        GPIO.output(4,0)
        GPIO.output(17,1)
        GPIO.output(27,0)
        
    elif rele == 4:
        # print ("\tCarga OFF: 4 \n\tCargas ON: 1,2,3 TestLoad")
        GPIO.output(3,0)
        GPIO.output(4,0)
        GPIO.output(17,0)
        GPIO.output(27,1)

    elif rele == 5:
        # print ("\tCarga OFF: TestLoad \n\tCargas ON: 1,2,3 e 4")
        GPIO.output(3,0)
        GPIO.output(4,0)
        GPIO.output(17,0)
        GPIO.output(27,0)
        
    else:
        print ("\tOpcao Invalida")

    

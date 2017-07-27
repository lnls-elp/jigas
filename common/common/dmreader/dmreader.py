'''
pip3 install pylibdmtx
pip3 install pylibdmtx[scripts]
pip3 install opencv-python
'''

import cv2
from pylibdmtx.pylibdmtx import decode

def ReadDataMatrix(frameWidth = 640, frameHeight = 480, cropSize = 220):

    print('*************************************************************************')
    print('Posicione o barcode dentro do quadrado e selecione uma das opções abaixo:')
    print('*************************************************************************')
    print('\nSPACE: Ler etiqueta')
    print('ESC: Cancelar')

    # Scan area parameters
    y0 = int((frameHeight-cropSize)/2)
    yEnd = int((frameHeight+cropSize)/2)
    x0 = int((frameWidth-cropSize)/2)
    xEnd = int((frameWidth+cropSize)/2)
    horizLine = [0 for val in range(x0,xEnd)]
    vertLine = [0 for val in range(y0,yEnd)]

    # Webcam initialization
    cam = cv2.VideoCapture(0)
    cam.set(3,frameWidth)
    cam.set(4,frameHeight)

    while True:
        # Read and process frame
        ret_val, img = cam.read()
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img = cv2.flip(img, 0)
        img = cv2.flip(img, 1)

        # Crop frame to scan area
        crop_img = img[y0:yEnd,x0:xEnd]

        # Draw scan area
        img[y0:yEnd,x0] = vertLine
        img[y0:yEnd,xEnd] = vertLine
        img[y0,x0:xEnd] = horizLine
        img[yEnd,x0:xEnd] = horizLine

        # Show video
        cv2.imshow('Place barcode inside the square', img)

        # Esc to quit
        # Space to read barcode
        pressedKey = cv2.waitKey(1)
        if pressedKey != 255:
            print(pressedKey)
        #if pressedKey == 81 or pressedKey == 113:
        if pressedKey == 27:
            data = None
            break
        #elif pressedKey == 67 or pressedKey == 99:
        elif pressedKey == 32:
            data = decode(crop_img)
            if data == []:
                print('Tente novamente...')
            else:
                data = int(decode(crop_img)[0].data)
                break

    # Release camera application
    cam.release()
    cv2.destroyAllWindows()
    return data

#def main():
#    data = ReadDataMatrix()
#    if data == None:
#        print('Leitura cancelada')
#    else:
#        print('Serial-Number lido: ' + str(data))
#
#if __name__ == '__main__':
#    main()

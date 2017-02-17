import numpy as np
import cv2
import serial
import time
import pygame
import sys 
from pygame.locals import *
import math as math
from helper import *




###############################################################################################
# WANT TO: initialize important hardware
###############################################################################################

#ser = serial.Serial('/dev/ttyUSB0', baudrate=38400, bytesize=8, parity='N', stopbits=1,timeout=0.001)
#print ser.isOpen()

cap = cv2.VideoCapture('output_02_06_1611_ct3_delay30.avi')
#cap = cv2.VideoCapture(1)
'''
# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_gray_01_20_16_25_ct7.avi',fourcc, 20.0, (640,480))
'''

###############################################################################################
# WANT TO: deal with new frame
###############################################################################################

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        car_mark = 0


        # write the flipped frame
        #
        #
        # out.write(frame)
        

        cv2.imshow('frame',frame)
        cv2.imwrite('./img/frame_1.jpg', frame)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
#out.release()
cv2.destroyAllWindows()
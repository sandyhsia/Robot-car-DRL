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
# WANT TO: initialize important param_s
###############################################################################################

car_center_pre = car_center = (0, 0)
mark1_center_pre = mark1_center = (0, 0)
mark2_center_pre = mark2_center = (0, 0)
car_cnt = car_cnt_pre = 0


frame_counter = 0
turnAngle_pre = 0
turnAngle = 0

target_point = (350, 300)
car_body_d = 30 # diameter
init_direction = 90 # default value

is_arrival = 0
current_direction = init_direction


color = 125,100,210
# rect_list=[100,100,20,20] #left, top, width, height
head = [0,0]
tail = [0,0]
center = [0, 0]
pi = 3.1415926
angle = pi/2

command_counter = 0


###############################################################################################
# WANT TO: initialize important hardware
###############################################################################################

ser = serial.Serial('/dev/ttyUSB0', baudrate=38400, bytesize=8, parity='N', stopbits=1,timeout=0.001)
print ser.isOpen()

# cap = cv2.VideoCapture('output_01_20_16_22.avi')
cap = cv2.VideoCapture(1)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_02_07_1625_ct3_delay30.avi',fourcc, 20.0, (640,480))


###############################################################################################
# WANT TO: deal with new frame
###############################################################################################

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        car_mark = 0


        ###############################################################################################
        # WANT TO: determinate car_mark, car_center, turn_angle
        ###############################################################################################

        print("--------------new frame--------------", frame_counter)
        ret, bin2 = cv2.threshold(gray, 128, 255, 8)
        # cv2.imshow("binary", bin2)

        # FindContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        (x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)
        # print(board_angle)
        # gray = cv2.drawContours(gray,[board_cnt],0,(128,0,0),2)
        
        rows,cols=gray.shape
        M0 = cv2.getRotationMatrix2D((cols/2,rows/2), board_angle, 1)
        gray = cv2.warpAffine(gray,M0,(cols,rows))
        
        ret, bin2 = cv2.threshold(gray, 128, 255, 8)
        cv2.imshow("binary", bin2)
        edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        (x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)

        
        leftmost = tuple(board_cnt[board_cnt[:,:,0].argmin()][0])
        rightmost = tuple(board_cnt[board_cnt[:,:,0].argmax()][0])
        topmost = tuple(board_cnt[board_cnt[:,:,1].argmin()][0])
        bottommost = tuple(board_cnt[board_cnt[:,:,1].argmax()][0])
        # print(leftmost)


        # should develop one ROI function
        roi = bin2[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
        crop_gray = gray[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
        
        #
        ret, bin3 = cv2.threshold(crop_gray, 128, 255, 8)
        edges, bin3_contours, hierarchy=cv2.findContours(bin3,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        cv2.imshow("bin3", bin3)
        


        frame_counter = frame_timer(frame_counter)    # every 4000 frames, clear it to 0 
        car_center_pre, car_cnt_pre, mark1_center_pre, mark2_center_pre, turnAngle_pre = car_info_backup(frame_counter, car_center, car_center_pre, car_cnt, car_cnt_pre, mark1_center, mark1_center_pre, mark2_center, mark2_center_pre, turnAngle, turnAngle_pre)
        
        car_center, car_cnt, mark1_center, mark2_center= car_pos_deter(bin3_contours)
        cv2.imshow("roi", roi)
        
        '''
        if cv2.pointPolygonTest(board_cnt, car_center, False) != 1:
            car_center = car_center_pre
            car_cnt = car_cnt_pre
        '''
    
        turnAngle = car_angle_deter(car_center, mark1_center, mark2_center)    #unit:degree

        if frame_counter != 0:
            car_stable = car_pos_is_table(car_center, car_center_pre, mark1_center, mark1_center_pre, mark2_center, mark2_center_pre, 40, turnAngle, turnAngle_pre, 40)
            print ("car_stable", car_stable)

            if car_stable != 1:
                car_center = car_center_pre
                car_cnt = car_cnt_pre
                mark1_center = mark1_center_pre
                mark2_center = mark2_center_pre
                turnAngle = turnAngle_pre
    

        ###############################################################################################
        # WANT TO: giving command to car
        ###############################################################################################
    
        distance = math.sqrt((target_point[0] - car_center[0])*(target_point[0] - car_center[0]) + (target_point[1] - car_center[1])*(target_point[1] - car_center[1]))
        cv2.circle(crop_gray, target_point, 1, (0,0,0), 20)
        command = 'w' # default command
        target_direction = vector_direction(car_center, target_point)
        current_direction = turnAngle + init_direction
    
        if distance > car_body_d:
            command = command_calculator(target_direction, current_direction, 15)

        else:
            is_arrival = 1
            command = 'q'

        command_counter = command_counter + 1
        if command_counter == 2:
            if is_arrival == 0:
                ser.write(command)
                print("counting counting")
            
            command_counter = 0

        
        ###############################################################################################
        # WANT TO: draw/print to test stability
        ###############################################################################################
        
        print(command)
        cv2.circle(crop_gray, (int(car_center[0]),int(car_center[1])), 1, (128,0,0), 3)
        cv2.circle(crop_gray, (int(mark1_center[0]),int(mark1_center[1])), 1, (255,0,0), 1)
        cv2.circle(crop_gray, (int(mark2_center[0]),int(mark2_center[1])), 1, (255,0,0), 1)
        print("current is:", current_direction)
        print("target is:", target_direction)
        print("turnAngle is:", turnAngle)







        # write the flipped frame
        #
        #
        out.write(frame)
        
        frame_counter = frame_counter + 1

        cv2.imshow('frame',frame)
        cv2.imshow('gray',gray)
        cv2.imshow('crop_gray',crop_gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
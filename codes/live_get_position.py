import numpy as np
import cv2
import serial
import time
import pygame
import sys 
from pygame.locals import *
import math as math
from helper_Feb09 import *

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
count_index = 0
car_x_sum = car_y_sum = 0

###############################################################################################
# WANT TO: deal with new frame
###############################################################################################
cap = cv2.VideoCapture(1)

# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('position_error_test.avi',fourcc, 20.0, (640,480))


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)


        ###############################################################################################
        # WANT TO: determinate car_mark, car_center, turn_angle
        ###############################################################################################

        print("--------------new frame--------------", frame_counter)
        ret, bin2 = cv2.threshold(gray, 128, 255, 8)
        cv2.imshow("bin2", bin2)

        bin2_tmp = cv2.copyMakeBorder(bin2,0,0,0,0,cv2.BORDER_REPLICATE)

        edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        (x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)

        '''
        left_top = find_corner(bin2_tmp, (int(x-w/2), int(y-h/2)), 30, 1, 255)
        right_top = find_corner(bin2_tmp, (int(x+w/2), int(y-h/2)), 30, 2, 255)
        left_bottom = find_corner(bin2_tmp, (int(x-w/2), int(y+h/2)), 30, 3, 255)
        right_bottom = find_corner(bin2_tmp, (int(x+w/2), int(y+h/2)), 30, 4, 255)
        '''
        left_top = (int(x-w/2), int(y-h/2))
        right_top = (int(x+w/2), int(y-h/2))
        left_bottom = (int(x-w/2), int(y+h/2))
        right_bottom = (int(x+w/2), int(y+h/2))

        pts1 = np.float32([[left_top,right_top,left_bottom,right_bottom]])
        pts2 = np.float32([[0,0],[int(round(w)),0],[0,int(round(h))],[int(round(w)),int(round(h))]])

        M = cv2.getPerspectiveTransform(pts1,pts2)

        print(int(round(h)),int(round(w)))
        gray_dst = cv2.warpPerspective(gray,M,(int(round(w)),int(round(h))))
        cv2.imshow("gray_dst", gray_dst)

        ret, bin2_dst = cv2.threshold(gray_dst, 100, 255, 0)

        cv2.imshow("bin2_dst", bin2_dst)

        edges, contours_dst, hierarchy=cv2.findContours(bin2_dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        frame_counter = frame_timer(frame_counter)    # every 4000 frames, clear it to 0 
        car_center_pre, car_cnt_pre, mark1_center_pre, mark2_center_pre, turnAngle_pre = car_info_backup(frame_counter, car_center, car_center_pre, car_cnt, car_cnt_pre, mark1_center, mark1_center_pre, mark2_center, mark2_center_pre, turnAngle, turnAngle_pre)
        
        print(len(contours_dst))
        car_center, car_cnt, mark1_center, mark2_center= car_pos_deter(contours_dst)
        print("car_center", car_center)

        print("mark1_center", mark1_center)
        print("mark2_center", mark2_center)
        gray_dst = cv2.drawContours(gray_dst,[car_cnt],0,(128,0,0),2)
        
        cv2.circle(gray_dst, (int(car_center[0]),int(car_center[1])), 1, (0,0,0), 1)
        cv2.circle(gray_dst, (int(mark1_center[0]),int(mark1_center[1])), 1, (255,0,0), 1)
        cv2.circle(gray_dst, (int(mark2_center[0]),int(mark2_center[1])), 1, (255,0,0), 1)
        
        if car_center[0] != 0 or car_center[1] != 0:
            count_index += 1
            car_x_sum += car_center[0]
            car_y_sum += car_center[1]

        cv2.imshow("gray_dst", gray_dst)
        
        #print(float(car_x_sum/count_index), float(car_y_sum/count_index))
        '''
        print("error", float((134.5+16.4285+3.2917 - car_center[0])))
        '''

        frame_counter += 1

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break
    
    else:
        break

# Release everything if job is finished
cap.release()

#out.release()
cv2.destroyAllWindows()
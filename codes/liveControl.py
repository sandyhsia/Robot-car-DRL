import numpy as np
import cv2
import serial
import time
import pygame
import sys 
from pygame.locals import *
import math as math


###############################################################################################
# WANT TO: initialize important param_s
###############################################################################################

M1_x_pre = M1_x = 0
M1_y_pre = M1_y = 0
M2_x_pre = M2_x = 0
M2_y_pre = M2_y = 0
M3_x_pre = M3_x = 0
M3_y_pre = M3_y = 0

circle_center = (M1_x, M1_y)
circle_center_pre = (M1_x_pre, M1_y_pre)
cnt_pre = 0

turnAngle_pre = 0
turnAngle = 0

target_point = (300, 30)
car_body_d = 50 # diameter
init_direction = 90

isArrival = 0


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
  
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Keyboard Demo")
pygame.key.set_repeat(50)
pygame.draw.line(screen, [255,0,0], [0,0], [50,50], 5)
pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)
cap = cv2.VideoCapture(1)


# Define the codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output_gray_01_20_16_25_ct7.avi',fourcc, 20.0, (640,480))



###############################################################################################
# WANT TO: deal with new frame
###############################################################################################

while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
        #frame = cv2.flip(frame,0)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        car_mark = 0


        ###############################################################################################
        # WANT TO: determinate car_mark, car_center, turn_angle
        ###############################################################################################

        print("--------------new frame--------------")
        #
        binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 5)
        ret, bin2 = cv2.threshold(gray, 128, 255, 8)
        #adaptive_method = ADAPTIVE_THRESH_MEAN_C, threshold_type=THRESH_BINARY, block_size=3, param1=5
        # edges = cv2.Canny(img, 20, 150, apertureSize = 3)
        cv2.imshow("binary", bin2)


        # FindContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  
        edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        
        
        #print(hierarchy)

        rectMax_area = 0
        rectMax_num = 0
        actual_angle_2 = 0
        actual_angle_3 = 0

        if circle_center != (0, 0):
            circle_center_pre = circle_center
            cnt_pre = cnt
        if turnAngle != 0 or turnAngle_pre !=0:
            turnAngle_pre = turnAngle
        
        # get largest rect, area ~= 120000
        outer_index = 0
        while(cv2.contourArea(contours[outer_index]) < 50000):
            outer_index = outer_index + 1
            
        cv2.drawContours(gray, contours, outer_index,(255,0,0),3)


        outer_cnt = contours[outer_index]
        for i in range(0, len(contours)):
            cnt = contours[i]
            cntarea = cv2.contourArea(cnt, 0)
            if cntarea > 500 and cntarea < 820: 
                # If the contour is approx rectangle 
                # area = cv2.contourArea(cnt)
                '''
                x,y,w,h = cv2.boundingRect(cnt)
                rect_area = w*h
                extent = float(cntarea)/rect_area
                '''
                
                rect = cv2.minAreaRect(cnt)
                (x,y),(w,h), angle = rect
                rect_area = w*h
                extent = float(cntarea)/rect_area

                if extent >= 0.9:
                    if cntarea > rectMax_area:
                        rectMax_area = cntarea
                        rectMax_num = i
                        # cv2.drawContours(gray, contours, i,(255,0,0),3)


        # print(cv2.contourArea(contours[rectMax_num]))
        # print(cv2.matchShapes(outer_cnt, contours[rectMax_num], 1, 0.0))
        # print(cv2.contourArea(contours[rectMax_num], 0))


        # calulate mass center(cx, cy), rectangle center(x+w/2, y+h/2)
        cnt = contours[rectMax_num]
        ######M1 = cv2.moments(cnt)
        ######M1_x = int(M1['m10']/M1['m00'])
        ######M1_y = int(M1['m01']/M1['m00'])
        M1_x = int(x)
        M1_y = int(y)
        circle_center = (M1_x,M1_y)
        # print(circle_center)
    
        if cv2.pointPolygonTest(outer_cnt, circle_center, False) == -1:
            circle_center = circle_center_pre
            cnt = cnt_pre
    

        #cv2.drawContours(gray, [cnt], 0, (255,0,0),1) # gray outline
        #cv2.circle(gray, circle_center, 2, (0,0,0),1) # black circle


        cnt1 = contours[rectMax_num]

        for i in range(0, len(contours)):
            cnt2 = contours[i]
            cnt2area = cv2.contourArea(cnt2, 0)
            if  cnt2area > 50 and cnt2area < 100:
                M2 = cv2.moments(cnt2)
                #print M
                M2_x = int(M2['m10']/M2['m00'])
                M2_y = int(M2['m01']/M2['m00'])
                circle_center = (M2_x,M2_y)
                #print(circle_center)
                if cv2.pointPolygonTest(cnt1, circle_center, False) == 1:
                    cv2.circle(gray, circle_center, 1, (128,0,0), 1)
                    cv2.line(gray, (M2_x, M2_y), (M1_x, M1_y), (200, 0, 0), 1)

                    print("large")
                    print((M1_x, M1_y))
                    print((M2_x, M2_y))
                    actual_angle_2 = math.atan2(-(M2_y - M1_y), (M2_x - M1_x))
                    print((actual_angle_2/3.1415926)*180)



            elif  cnt2area > 20 and cnt2area < 50:
                M3 = cv2.moments(cnt2)
                #print M
                M3_x = int(M3['m10']/M3['m00'])
                M3_y = int(M3['m01']/M3['m00'])
                circle_center = (M3_x,M3_y)
                #print(circle_center)
                if cv2.pointPolygonTest(cnt1, circle_center, False) == 1:
                    cv2.circle(gray, circle_center, 1, (128,0,0), 1)
                    cv2.line(gray, (M3_x, M3_y), (M1_x, M1_y), (200, 0, 0), 1)

                    print("small")
                    print((M1_x, M1_y))
                    print((M3_x, M3_y))
                    actual_angle_3 = math.atan2(-(M3_y - M1_y), (M3_x - M1_x))
                    print((actual_angle_3/3.1415926)*180)
                    # print(gray[M2_x, M2_y])
    
    
        turnAngle = (actual_angle_2/3.1415926)*180 - 45 - init_direction    #unit:degree
        if turnAngle - turnAngle_pre > 50 or turnAngle - turnAngle_pre < -50:
            turnAngle = turnAngle_pre

        print("turnAngle:")
        print(turnAngle)

        car_mark = 3 - 2*bin2[M2_x, M2_y] - 1*bin2[M3_x, M3_y]
        print("car_mark:")
        print(car_mark)
    

        ###############################################################################################
        # WANT TO: giving command to car
        ###############################################################################################
    
        distance = math.sqrt((target_point[0] - M1_x)*(target_point[0] - M1_x) + (target_point[1] - M1_y)*(target_point[1] - M1_y))
        cv2.circle(gray, target_point, 1, (0,0,0), 20)
        command = 'w'
    
        if distance > car_body_d: 
            target_direction = (math.atan2(-target_point[1]+M1_y, target_point[0]-M1_x))/3.1415926*180
            current_direction = turnAngle + init_direction
            print(target_direction)
            print(current_direction)
        
            if (target_direction - current_direction <= 30 and target_direction - current_direction >=0) or (target_direction - current_direction >= -30 and target_direction - current_direction <= 0):
                command = 'w'
        
            elif target_direction - current_direction <= -150 and target_direction - current_direction >= -210:
                command = 's'

            elif (target_direction - current_direction > 30 and target_direction - current_direction < 90) or (target_direction - current_direction > -210 and target_direction - current_direction < -270):
                command = 'a'

            elif target_direction - current_direction < -30 and target_direction - current_direction > -150:
                command = 'd'
        else:
            isArrival = 1
            command = 'q'
    
        print(command)

        # ser.reset_output_buffer()
        command_counter = command_counter + 1
        if command_counter == 7:
            if isArrival == 0:
                ser.write(command)
            
            command_counter = 0



        # write the flipped frame
        out.write(gray)

        cv2.imshow('frame',frame)
        cv2.imshow('gray',gray)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()
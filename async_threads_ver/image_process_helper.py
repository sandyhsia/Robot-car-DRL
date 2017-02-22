import numpy as np
import cv2
import time
import sys 
import math as math
from helper_Feb16 import *

def cut_restore(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    ret, bin2 = cv2.threshold(gray, 128, 255, 8)
    # cv2.imshow("bin2", bin2)

    # bin2_tmp = cv2.copyMakeBorder(bin2,0,0,0,0,cv2.BORDER_REPLICATE)
    contours, hierarchy = cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    (x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours) # return position and angle of the board

    left_top = (int(x-w/2), int(y-h/2))
    right_top = (int(x+w/2), int(y-h/2))
    left_bottom = (int(x-w/2), int(y+h/2))
    right_bottom = (int(x+w/2), int(y+h/2))

    pts1 = np.float32([[left_top,right_top,left_bottom,right_bottom]])
    pts2 = np.float32([[0,0],[int(round(w)),0],[0,int(round(h))],[int(round(w)),int(round(h))]])

    M = cv2.getPerspectiveTransform(pts1,pts2)

    # print(int(round(h)),int(round(w)))
    gray_dst = cv2.warpPerspective(gray,M,(int(round(w)),int(round(h))))
    #cv2.imshow("gray_dst", gray_dst)

    ret, bin2_dst = cv2.threshold(gray_dst, 100, 255, 0)
    # find the cars' contour on the board
    contours_dst, hierarchy=cv2.findContours(bin2_dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

    return gray_dst, contours_dst

def car_info_get(contours_dst):     
    if(len(contours_dst) <= 0):
        car_center = mark1_center = mark2_center = (0, 0)
    else: 
        car_center, car_cnt, mark1_center, mark2_center = car_pos_deter(contours_dst)

    return car_center, mark1_center, mark2_center

def  two_point_distance(start_pt, end_pt):
    return  math.sqrt((start_pt[0] - end_pt[0])**2 + (start_pt[1] - end_pt[1])**2)
        
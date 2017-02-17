import numpy as np
import cv2
import time
import sys 
import math as math
from helper_Feb09 import *

    def cut_restore(frame):

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, bin2 = cv2.threshold(gray, 128, 255, 8)
        # cv2.imshow("bin2", bin2)

        bin2_tmp = cv2.copyMakeBorder(bin2,0,0,0,0,cv2.BORDER_REPLICATE)
        edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        (x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)

        left_top = find_corner(bin2_tmp, (int(x-w/2), int(y-h/2)), 20, 1, 255)
        right_top = find_corner(bin2_tmp, (int(x+w/2), int(y-h/2)), 20, 2, 255)
        left_bottom = find_corner(bin2_tmp, (int(x-w/2), int(y+h/2)), 20, 3, 255)
        right_bottom = find_corner(bin2_tmp, (int(x+w/2), int(y+h/2)), 20, 4, 255)

        pts1 = np.float32([[left_top,right_top,left_bottom,right_bottom]])
        pts2 = np.float32([[0,0],[int(round(w)),0],[0,int(round(h))],[int(round(w)),int(round(h))]])

        M = cv2.getPerspectiveTransform(pts1,pts2)

        # print(int(round(h)),int(round(w)))
        gray_dst = cv2.warpPerspective(gray,M,(int(round(w)),int(round(h))))
        # cv2.imshow("gray_dst", gray_dst)

        ret, bin2_dst = cv2.threshold(gray_dst, 100, 255, 0)
        edges, contours_dst, hierarchy=cv2.findContours(bin2_dst,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        return gray_dst, contours_dst

    def car_info_get(contours_dst):
        
    	if(len(contours_dst) <= 0):
            car_center = mark1_center = mark2_center = (0, 0)

        else: 
            car_center, car_cnt, mark1_center, mark2_center = car_pos_deter(contours_dst)

        return car_center, mark1_center, mark2_center
        
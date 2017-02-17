import numpy as np
import cv2
import serial
import time
import pygame
import sys 
from pygame.locals import *
import math as math
from helper import *

frame = cv2.imread("./img/frame_1.jpg")
cv2.imshow("frame", frame)

gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
ret, bin2 = cv2.threshold(gray, 128, 255, 8)

bin2_tmp = cv2.copyMakeBorder(bin2,0,0,0,0,cv2.BORDER_REPLICATE)
print(bin2_tmp.shape)
print(bin2.shape)

cv2.imshow("bin2", bin2)
cv2.imshow("bin2_tmp", bin2_tmp)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(1)

edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
(x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)

print("draw right")

cv2.circle(gray, (int(x+w/2), int(y-h/2)), 1, (128,0,0), 3)
print((int(x+w/2), int(y-h/2)))

left_top = find_corner(bin2_tmp, (int(x-w/2), int(y-h/2)), 30, 1, 255)
right_top = find_corner(bin2_tmp, (int(x+w/2), int(y-h/2)), 30, 2, 255)
left_bottom = find_corner(bin2_tmp, (int(x-w/2), int(y+h/2)), 30, 3, 255)
right_bottom = find_corner(bin2_tmp, (int(x+w/2), int(y+h/2)), 30, 4, 255)

cv2.circle(gray, left_top, 1, (255,0,0), 3)
cv2.imshow("gray", gray)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(100)

cv2.circle(gray, right_top, 1, (255,0,0), 3)
cv2.imshow("gray", gray)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(100)

cv2.circle(gray, left_bottom, 1, (255,0,0), 3)
cv2.imshow("gray", gray)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(100)

cv2.circle(gray, right_bottom, 1, (255,0,0), 3)
cv2.imshow("gray", gray)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(100)

pts1 = np.float32([[left_top,right_top,left_bottom,right_bottom]])
pts2 = np.float32([[0,0],[int(round(w)),0],[0,int(round(h))],[int(round(w)),int(round(h))]])

M = cv2.getPerspectiveTransform(pts1,pts2)

dst = cv2.warpPerspective(gray,M,(int(round(w)),int(round(h))))
cv2.imshow("dst", dst)
if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(100)




'''
rows,cols=bin2.shape
M0 = cv2.getRotationMatrix2D((cols/2,rows/2), board_angle, 1)
gray = cv2.warpAffine(gray,M0,(cols,rows))
bin2 = cv2.warpAffine(bin2,M0,(cols,rows))

edges, contours, hierarchy=cv2.findContours(bin2,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
(x,y), (w,h), board_angle, board_cnt = board_pos_deter(contours)

        
leftmost = tuple(board_cnt[board_cnt[:,:,0].argmin()][0])
rightmost = tuple(board_cnt[board_cnt[:,:,0].argmax()][0])
topmost = tuple(board_cnt[board_cnt[:,:,1].argmin()][0])
bottommost = tuple(board_cnt[board_cnt[:,:,1].argmax()][0])
# print(leftmost)

# should develop one ROI function
crop_gray = gray[topmost[1]:bottommost[1], leftmost[0]:rightmost[0]]
        
#
ret, bin3 = cv2.threshold(crop_gray, 128, 255, 8)
cv2.imshow("bin3", bin3)
        


cv2.imshow("crop_gray", crop_gray)
'''
cv2.imshow("gray", gray)
cv2.imshow("bin2", bin2)
cv2.imshow("bin2_tmp", bin2_tmp)

if cv2.waitKey(0) & 0xFF == ord('q'):
    cv2.waitKey(1)
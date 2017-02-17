#!/usr/bin/python
# -*- coding: UTF-8 -*-

import Queue
import threading
import time
import cv2
import numpy as np
import pygame
import sys 
import math as math
import socket
from image_process_helper import *
from RBcar_helper import *

exitFlag = 0
test_frame_counter = 0
counted_num = 0
car_center = mark1_center = mark2_center = (0,0)
car_center_test_sum = mark1_center_test_sum = mark2_center_test_sum = (0,0)
routeList = [(100, 300)]
target_point_index = 0


class cameraThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        img2command(self.name, self.q)
        print "Exiting " + self.name



class socketThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print "Starting " + self.name
        command2server(self.name, self.q)
        print "Exiting " + self.name


def img2command(threadName, q):
    cap = cv2.VideoCapture(1)
    cap.set(3,1080)        ###wide
    cap.set(4,720)         ###height
    
    agent = RBcar((0,0), (0,0), (0,0), routeList[0])
    agent.clear()
    target_point_index = 1

    while not exitFlag:
        print(cap.isOpened())
        time.sleep(1)

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:

                gray_dst, contours_dst=cut_restore(frame)
                
                

                ''' Initialize the car agent position'''

                if(test_frame_counter < 20):
                    car_center, mark1_center, mark2_center = car_info_get(contours_dst)

                    if(car_center != (0,0) and mark1_center != (0,0) and mark2_center != (0,0)):
                        car_center_test_sum += car_center
                        mark1_center_test_sum += mark1_center
                        mark2_center_test_sum += mark2_center
                        counted_num += 1

                    if(counted_num > 0):
                        agent.car_center = car_center_test_sum / counted_num
                        agent.mark1_center = mark1_center_test_sum / counted_num
                        agent.mark2_center = mark2_center_test_sum / counted_num


                    test_frame_counter += 1
                
                
                else:
                    if(test_frame_counter == 20):
                        agent.car_mark1_distance = two_point_distance(self.car_center, self.mark1_center)
                        agent.car_mark2_distance = two_point_distance(self.car_center, self.mark2_center)

                    car_center, mark1_center, mark2_center = car_info_get(contours_dst)
                    agent.set_CarCenter(car_center)
                    agent.set_Mar1Center(mark1_center)
                    agent.set_Mar1Center(mark2_center)
                    agent.check_and_try_restore()
                    '''
                    if(agent.is_arrival() == 1):
                        agent.set_TargetPoint(routeList[target_point_index])
                        agent.update(average_speed)
                    '''
                
                if(test_frame_counter >= 20):
                    print ("car_center:", agent.car_center)
                    print ("mark1_center:", agent.mark1_center)
                    print ("mark2_center:", agent.mark2_center)
                    
                    cv2.circle(gray_dst, (int(agent.car_center[0]),int(agent.car_center[1])), 2, (128,0,0),1) # black circle
                    cv2.circle(gray_dst, (int(agent.mark1_center[0]),int(agent.mark1_center[1])), 2, (128,0,0),1) # black circle
                    cv2.circle(gray_dst, (int(agent.mark2_center[0]),int(agent.mark2_center[1])), 2, (128,0,0),1) # black circle
                    
                    
                    queueLock.acquire()
                    if(q.full() != 1):
                        q.put("c3+w255q")
                        # q.put(instruction)
                    queueLock.release()

                cv2.imshow('frame',frame)
                cv2.imshow('gray_dst',gray_dst)
                cv2.waitKey(0)


                if exitFlag:
                	break
            else:
                break

    # Release everything if job is finished
    cap.release()
    #out.release()
    cv2.destroyAllWindows()



def command2server(threadName, q):
    while not exitFlag:
        HOST = ''               # Symbolic name meaning all available interfaces
        PORT = 5678             # Arbitrary non-privileged port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        print 'Connected by', addr
        while 1:
            # data = conn.recv(1024)
            if exitFlag: break
            else:
                queueLock.acquire()
                if(q.empty() != True):
                    command_data = q.get()
                queueLock.release()
                # print "%s processing %s" % (threadName, command_data)
            
                time.sleep(0.03)
                conn.sendall(command_data)
                # print command_data
        conn.close()





#############################################################################
#############################################################################

threadList1 = ["camera-Thread"]
threadList2 = ["server-Thread"]
nameList = ["c3+s255q", "c3+s255q", "c3+s255q", "c3+s255q", "c3+s255q"]
queueLock = threading.Lock()
workQueue = Queue.Queue(10)
threads = []
threadID = 1

# 创建新线程
try:
    for tName in threadList1:
        thread = cameraThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    '''
    for tName in threadList2:
        thread = socketThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    '''

    # 填充队列
    queueLock.acquire()
    for word in nameList:
        workQueue.put(word)
        print "putting word:", word
    queueLock.release()

    

    error = raw_input('input q when you want to quit:')
    if error=='q':
        raise KeyboardInterrupt('quit!')


except KeyboardInterrupt, msg:
    print msg
    exitFlag = 1

# 通知线程是时候退出
# exitFlag = 1

# 等待所有线程完成
for t in threads:
    t.join()
print "Exiting Main Thread"
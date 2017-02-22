#!/usr/bin/python
# -*- coding: UTF-8 -*-

import Queue
import thread
import threading
import time
import cv2
import numpy as np
import pygame
import sys
import signal
import math
import socket
import numpy as np

from image_process_helper import *
from RBcar_helper import *
from helper_Feb16 import *
#from PID_helper import *

exitFlag = 0



class cameraThread (threading.Thread):
        def __init__(self, threadID, name, command_q, feedback_q):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.command_q = command_q
                self.feedback_q = feedback_q
                self.loopcounter = 0
                self._running = True
                self._knowServerAlive = False


                self.instruction_backup = self.instruction_to_give = self.command_last = 'c3+w010q' 
                '''backup command for last frame; 
                   instruction-to-give is updated in current frame; 
                   command_last related to last command put into command queue
                   In this way, backup rate should be faster than recording command_last'''

                self.routeList = [(300, 200)]
                self.testmode_arr = {"car_center_test_sum":0,   "car_center_valid_time":0,  "mark1_center_test_sum":0,  "mark1_center_valid_time":0,    "mark2_center_test_sum":0,  "mark2_center_valid_time":0}
                self.agent =  RBcar((0,0), (0,0), (0,0), routeList[0])
                self.agent.clear()

                return
        
        def terminate(self):
                print "trying to terminate camera thread"
                self._running = False
                #sys.exit(0)
                return
        
        def run(self):
                print "Starting " + self.name
                cap= self.cam_init()
                while self._running:
                        self.loopcounter = self.loopcounter+1
                        print "loop:"+str(self.loopcounter)+", cam:self running is " + str(self._running)
                        self.cam_mainloop(cap, self.loopcounter, testmode_arr)
                        self.img2command(self.name, self.command_q, self.feedback_q, self.instruction_to_give)
                        time.sleep(0.025)
                print "Exiting " + self.name
                return
    
        def cam_init(self):
                cap = cv2.VideoCapture(0)
                #cap.set(3,1080)        ###wide
                #cap.set(4,720)         ###height

                return cap
    
        def cam_mainloop(self, cap, frame_counter):
                ret, frame = cap.read()
                if ret==True:

                        # find the board, and contours on the board
                        gray_dst, contours_dst=cut_restore(frame)
                        car_center, mark1_center, mark2_center = car_info_get(contours_dst)

                        cv2.circle(gray_dst, (int(car_center[0]),int(car_center[1])), 2, (128,0,0),1) # black circle ''' ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''HERE!!!! frame should be gray_dst
                        cv2.circle(gray_dst, (int(mark1_center[0]),int(mark1_center[1])), 2, (128,0,0),1) # black circle
                        cv2.circle(gray_dst, (int(mark2_center[0]),int(mark2_center[1])), 2, (128,0,0),1) # black circle


                        if(frame_counter <= 200):
                                print "less than 200!"

                                
                                if(car_center != (0,0)):
                                        self.testmode_arr["car_center_test_sum"] += car_center
                                        self.testmode_arr["car_center_valid_time"] +=1

                                if(mark1_center != (0,0)):
                                        self.testmode_arr["mark1_center_test_sum"] += mark1_center
                                        self.testmode_arr["mark1_center_valid_time"] +=1

                                if(mark2_center != (0,0)):
                                        self.testmode_arr["mark2_center_test_sum"] += mark2_center
                                        self.testmode_arr["mark2_center_valid_time"] +=1
                                

                        if(frame_counter == 200):
                                
                                self.agent.car_center = self.testmode_arr["car_center_test_sum"] / self.testmode_arr["car_center_valid_time"]
                                self.agent.mark1_center = self.testmode_arr["mark1_center_test_sum"] / self.testmode_arr["mark1_center_valid_time"]
                                self.agent.mark2_center = self.testmode_arr["mark2_center_test_sum"] / self.testmode_arr["mark2_center_valid_time"]
                                self.agent.full_backup()
                                
                                print "less than 200 is ", (frame_counter <= 200)
                                cv2.circle(gray_dst, (int(self.agent.car_center[0]),int(self.agent.car_center[1])), 2, (128,0,0),5) # black circle ''' ''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''HERE!!!! frame should be gray_dst
                                cv2.circle(gray_dst, (int(self.agent.mark1_center[0]),int(self.agent.mark1_center[1])), 2, (128,0,0),5) # black circle
                                cv2.circle(gray_dst, (int(self.agent.mark2_center[0]),int(self.agent.mark2_center[1])), 2, (128,0,0),5) # black circle

                        elif(frame_counter > 200):

                                average_diff_distance = (two_point_distance(self.car_center_backup, car_center) + two_point_distance(self.mark1_center_backup, mark1_center) + two_point_distance(self.mark2_center_backup, mark2_center))/3
                                
                                if(average_diff_distance >= 100):
                                        self.agent.car_center = car_center
                                        self.agent.mark1_center = mark1_center
                                        self.agent.mark2_center = mark2_center
                                        self.agent.full_backup()


                                current_angle = self.agent.car_angle_deter(self.agent.car_center, self.agent.mark1_center, self.agent.mark2_center)
                                #print("angle", current_angle)
                                distance = two_point_distance(self.agent.car_center, self.agent.target_point)
                                command = 'w' # default command
                                target_direction = vector_direction(self.agent.car_center, self.agent.target_point)
                                car_pwm = 255

                                if distance > 30:
                                        command = command_calculator(target_direction, current_angle, 5)
                                        #print("direction:",target_direction)

                                        if(command == 'a' or command =='d'):
                                                car_pwm = int(abs(target_direction-current_angle)*0.6) + 150
                    
                                                if (car_pwm >= 255):
                                                        car_pwm = 255
                        
                                        #print("pwm:",car_pwm)
                                        #print("PIDoutput:", carPID.output)

                                else:
                                        command = 'x'
                                

                                #print(command)
                                instruction = 'c3+'+command+str(car_pwm)+'q'
                                print("instruction", instruction)

                                self.instruction_backup = self.instruction_to_give
                                self.instruction_to_give = instruction
                                                        

                                while(self._knowServerAlive == False):
                                        
                                        queueLock.acquire()
                                        if(self.feedback_q.empty() != 1):
                                                feedback = self.feedback_q.get()
                                                print "camera knows feedback:", feedback
                                                if(feedback == 'InitOk'):
                                                        self._knowServerAlive = True
                                                        self.command_q.put(self.instruction_to_give)
                                                        self.command_last = self.instruction_to_give
                                                        print "InitOK is:", self._knowServerAlive
                                                else:
                                                        self.feedback_q.put(feedback)
                                        queueLock.release()

                                        # print("know server alive:", self._knowServerAlive)

                        cv2.imshow('frame',frame)
                        cv2.imshow('gray_dst',gray_dst)


                        cv2.waitKey(25*((frame_counter <= 200) or self._knowServerAlive))
                        #print("know server alive:", self._knowServerAlive)
               

                return

        def img2command(self, threadName, command_q, feedback_q, instruction_to_give):

                queueLock.acquire()
                if(self._knowServerAlive == 1 and feedback_q.empty() != 1):
                        feedback = feedback_q.get()
                        print "camera knows feedback:", feedback
                        command_q.put(instruction_to_give)
                        self.command_last = instruction_to_give
                        queueLock.release()
                        return

                else:
                        queueLock.release()
                        return





class socketThread (threading.Thread):
        def __init__(self, threadID, name, command_q, feedback_q):
                threading.Thread.__init__(self)
                self.threadID = threadID
                self.name = name
                self.command_q = command_q
                self.feedback_q = feedback_q
                self._running = True
                self._conn = None
                self._initSuccess = False
                return
        
        def terminate(self):
                print "trying to terminate sockect thread"
                self._running = False
                if(self._initSuccess == True):
                        self._conn.shutdown(socket.SHUT_RD)
                        self._conn.close()
                #sys.exit(0)
                return
        
        def run(self):
                print "Starting " + self.name
                self._conn = self.server_init(self.command_q, self.feedback_q)
                while self._running:
                        self.server_process(self._conn)
                        print "network : self running is " + str(self._running)
                        #command2server(self.name, self.q,self._running)
                print "Exiting " + self.name
                return

        def server_init(self, command_q, feedback_q):
                print "server initialized done 1"
                HOST = ''               # Symbolic name meaning all available interfaces
                PORT = 5678             # Arbitrary non-privileged port
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.bind((HOST, PORT))
                s.listen(1)
                conn, addr = s.accept()
                print 'Connected by', addr
                data = conn.recv(4)
                print "Init-ing... receive: ", data

                if (data == 'c3c\n'):
                        knowServerAlive = True
                        queueLock.acquire()
                        if(feedback_q.empty() == True):
                                feedback_q.put("InitOk")
                                print "server put InitOk in feedback_q"
                        else:
                                feedback_q.get()
                                feedback_q.put("InitOk")

                        queueLock.release()
                        print "Server initialized done."
                        self._initSuccess = True
                return conn

        def server_process(self, conn):
                print "server processing 1"
                conn.settimeout(5)

                queueLock.acquire()
                if(self.command_q.empty() != True):
                        send_item = self.command_q.get()
                        conn.sendall(send_item)
                        sendout_time = time.time()
                        print "server sendout: ", send_item, " at ", sendout_time
                queueLock.release()

                try:
                        feedback_data = conn.recv(64)
                        queueLock.acquire()
                        if(self.feedback_q.empty() == True):
                                self.feedback_q.put(feedback_data)
                                queueLock.release()
                        else:
                                self.feedback_q.get()
                                self.feedback_q.put(feedback_data)
                                queueLock.release()
                        
                        #print "feedback time:", feedback_time
                        #print "difference in time:", (feedback_time - sendout_time)

                        print "get", feedback_data
                        time.sleep(0.13)

                except socket.timeout:
                        print "Server time out. Update..."
                
                return


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    thread1.terminate()
    thread2.terminate()
    time.sleep(1)
    sys.exit(0)


#############################################################################
#############################################################################

threadList1 = ["camera-Thread"]
threadList2 = ["server-Thread"]
nameList = ["c3+x255q"]
queueLock = threading.Lock()
Command_Q = Queue.Queue(1)
Feedback_Q = Queue.Queue(1)
threads = []
threadID = 1



# 填充队列
'''
queueLock.acquire()
    for word in nameList:
        workQueue.put(word)
        print "putting word:", word
    queueLock.release()
'''
    
thread1 = cameraThread(1, "camera-Thread", Command_Q, Feedback_Q)

thread2 = socketThread(2, "server-Thread", Command_Q, Feedback_Q)

thread1.start()
thread2.start()
threads.append(thread1)
threads.append(thread2)


while 1:
  signal.signal(signal.SIGINT, signal_handler)
  print "main thread processing"
  time.sleep(2)
  
for t in threads:
  t.join()
  
  
  
  
  #print "Exiting Main Thread"
  #time.sleep(1)

# 等待所有线程完成

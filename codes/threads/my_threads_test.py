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

exitFlag = 0


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
    cap = cv2.VideoCapture(0)
    cap.set(3,1080)        ###wide
    cap.set(4,720)         ###height
    
    while not exitFlag:
        print(cap.isOpened())
        time.sleep(1)

        while(cap.isOpened()):
            ret, frame = cap.read()
            if ret==True:
                cv2.imshow('frame',frame)
                cv2.waitKey(1)

                queueLock.acquire()
                if(q.full() != 1):
                    q.put("c3+w255q")
                queueLock.release()

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
                print "%s processing %s" % (threadName, command_data)
            
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

    for tName in threadList2:
        thread = socketThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    # 填充队列
    queueLock.acquire()
    for word in nameList:
        workQueue.put(word)
        print "putting word:", word
    queueLock.release()

    

    error = raw_input('input q when you want to quit:')
    if error=='q':
        raise ValueError('quit!')


except ValueError, msg:
    print msg
    exitFlag = 1

# 通知线程是时候退出
# exitFlag = 1

# 等待所有线程完成
for t in threads:
    t.join()
print "Exiting Main Thread"
#!/usr/bin/python
# -*- coding: UTF-8 -*-


import signal
import sys
import time
import thread



def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        sys.exit(0)
        
  #signal.pause()


#!/usr/bin/python
# -*- coding: UTF-8 -*-

import threading
import time
import sys

exitFlag = 0

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, counter):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.counter = counter
    def run(self):                   #把要执行的代码写到run函数里面 线程在创建后会直接运行run函数 
        print "Starting " + self.name
        print_time(self.name, self.counter, 5)
        print "Exiting " + self.name

def print_time(threadName, delay, counter):
    while counter:
        if exitFlag:
            thread.exit()
        time.sleep(delay)
        print "%s: %s" % (threadName, time.ctime(time.time()))
        counter -= 1

def signal_handler(signal, frame):
        print('You pressed Ctrl+C!')
        exitFlag = 1
        time.sleep(3)
        sys.exit(0)


# 创建新线程
thread1 = myThread(1, "Thread-1", 1)
thread2 = myThread(2, "Thread-2", 2)

# 开启线程
thread1.start()
thread2.start()

while 1:
  signal.signal(signal.SIGINT, signal_handler)
  print "main thread here"
  time.sleep(1)

print "Exiting Main Thread"

#!/usr/bin/python
#-*-coding:utf-8-*-
import time
import zmq

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5678")

while True:
    message = socket.recv(8)
    print message
    time.sleep(1)
    socket.send("server response!")
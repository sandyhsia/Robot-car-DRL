import serial
import time
import pygame
import sys 
import numpy as np
from pygame.locals import *


  
def key_event():
  press_key = ""
  for e in pygame.event.get():
    if e.type is not pygame.locals.KEYDOWN:
      return press_key

    if e.key == K_UP:
      press_key = "w"
    if e.key == K_DOWN:
      press_key = "s"
    if e.key == K_LEFT:
      press_key = "a"
    if e.key == K_RIGHT:
      press_key = "d"
    if e.key == K_ESCAPE:
      print "exiting!!!!"
      ser.close()
      time.sleep(0.2)
      sys.exit()
      
  return press_key




color = 125,100,210
rect_list=[100,100,20,20] #left, top, width, height
head = [400,500]
tail = [400,550]
center = [400, 525]
pi = 3.1415926
angle = pi/2

if __name__ == '__main__':
  #ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
  ser = serial.Serial('/dev/ttyUSB0', baudrate=38400, bytesize=8, parity='N', stopbits=1,timeout=0.001)
  print ser.isOpen()
  
  pygame.init()
  screen = pygame.display.set_mode((800, 600))
  pygame.display.set_caption("Keyboard Demo")
  pygame.key.set_repeat(50)
  pygame.draw.line(screen, [255,0,0], [0,0], [50,50], 5)
  pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)

  #for i in range(1,100000):
  #print "=================================="
  #ser.write("AT\r\n")
  while(1):
    
    press_key = key_event()
    if press_key!="":
      print press_key
    
    ser.write(press_key)
    #msg=ser.read(100)
    
    screen.fill(color)
    if press_key == 'a':
      print "drawing"
      angle = angle+pi/4
      head[0] = center[0] + 25*np.cos(angle)
      head[1] = center[1] - 25*np.sin(angle)
      
      tail[0] = center[0] + 25*np.cos(angle + pi)
      tail[1] = center[1] - 25*np.sin(angle + pi)
      
      pygame.draw.line(screen, [255,0,0], head, tail, 5)
      pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)
      print "head:",head[0],head[1]

    elif press_key == 'd':
      print "drawing"
      angle = angle - pi/4
      head[0] = center[0] + 25*np.cos(angle)
      head[1] = center[1] - 25*np.sin(angle)
      
      tail[0] = center[0] + 25*np.cos(angle + pi)
      tail[1] = center[1] - 25*np.sin(angle + pi)
      
      pygame.draw.line(screen, [255,0,0], head, tail, 5)
      pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)
      print "head:",head[0],head[1]

    elif press_key == 'w':
      print "drawing"
      #angle = angle
      center[0] = center[0] + 25*np.cos(angle)
      center[1] = center[1] - 25*np.sin(angle)
      head[0] = center[0] + 25*np.cos(angle)
      head[1] = center[1] - 25*np.sin(angle)
      tail[0] = center[0] + 25*np.cos(angle + pi)
      tail[1] = center[1] - 25*np.sin(angle + pi)
      pygame.draw.line(screen, [255,0,0], head, tail, 5)
      pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)
      print "head:",head[0],head[1]

    elif press_key == 's':
      print "drawing"
      #angle = angle
      center[0] = center[0] - 25*np.cos(angle)
      center[1] = center[1] + 25*np.sin(angle)
      head[0] = center[0] + 25*np.cos(angle)
      head[1] = center[1] - 25*np.sin(angle)
      tail[0] = center[0] + 25*np.cos(angle + pi)
      tail[1] = center[1] - 25*np.sin(angle + pi)
      pygame.draw.line(screen, [255,0,0], head, tail, 5)
      pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)
      print "head:",head[0],head[1]

    elif press_key == "":
      pygame.draw.line(screen, [255,0,0], head, tail, 5)
      pygame.draw.circle(screen, [0,0,0], (int(head[0]),int(head[1])), 3)

    pygame.display.update()


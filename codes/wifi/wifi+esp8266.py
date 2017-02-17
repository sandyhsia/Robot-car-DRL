import serial
import time
import sys 

c0="AT\r\n"
c1="AT+RST\r\n"
c2="AT+CWMODE=1\r\n"
c3="AT+CIPSTA=\"192.168.1.2\"\r\n"
c4="AT+CIFSR\r\n"
c5="AT+CWLAP\r\n"
c6="AT+CWJAP=\"iPhone\",\"sandy19941108\"\r\n"
c7="AT+CIPSTATUS\r\n"
c8="AT+CWJAP=\"hobot_ad\",\"0123456789\"\r\n"
c9="AT+CIPSTART=2,\"TCP\",\"192.168.1.100\",5678\r\n"
c10="AT+CIPSEND=2,4\r\n"
c="AT+CIPMUX=1\r\n"
d="AT+CIPSERVER=0\r\n"
string="1234\r\n"

if __name__ == '__main__':
  #ser = serial.Serial('/dev/ttyUSB0', 38400, timeout=1)
  ser = serial.Serial('/dev/ttyUSB0', baudrate=115200, bytesize=8, parity='N', stopbits=1,timeout=0.1)
  print ser.isOpen()
  #while(1):
  print "=================================="

  ser.write(c0)
  time.sleep(1)
  msg=ser.read(1000)
  print msg


  ser.write(c4)
  time.sleep(1)
  msg=ser.read(1000)
  print msg

  ser.write(c)
  time.sleep(1)
  msg=ser.read(1000)
  print msg

  ser.write(d)
  time.sleep(1)
  msg=ser.read(1000)
  print msg


  ser.write(c9)
  time.sleep(1)
  msg=ser.read(1000)
  print msg


  ser.write(c10)
  time.sleep(1)
  msg=ser.read(1000)
  print msg

  ser.write(string)
  time.sleep(1)
  msg=ser.read(1000)
  print msg

  ser.close()

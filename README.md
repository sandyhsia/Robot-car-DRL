# Robot-car-DRL


![view from top](Pics/bird_view.jpg)

#### More images about robot-car-agent, please go to /Pics/ :)

## 2017.02.23 ~ 2017.02.24: Version 0.1 Demo 
(Video might be uploaded soon)

### 1 Achievements:
> Using 'Easy PID + PWM Tuning'  to have a soft turning. 
> Implement async-threads communication. Using 2 shared 'Queues' to exchange 'instructions' and 'feedback' so that two threads can somehow have synchronization.

### 2.1 Hardware Problems
> My 'Arduino Uno R3' actually come from Taobao. 
> 1) 'AMS1117' chip on one board, which is used to convert input (~7.5 Volt now) to power arduino, has problem on pin voltage. 
> Result is that *this* Arduino Uno R3  can only use USB to set up power. (picture in Appendix/HardwareDocs)
> 2) 'LP2985' chip on another board, which is used to convert 5 Volt to 3.3 Volt as power pin, has problem...  
> Result is that 3.3 Volt power pin output is not stable (so that my esp8266 wifi module can't work). (picture in Appendix/HardwareDocs)

> Battery for motor-driving board is not powerful. Usually, it can drop from 10 Volt to 7 Volt.
> I must change the PWM params all the day in case to power up ENA/ENB (if input is lower than 2.8 Volt, than the motor won't move). Need to change.

### 2.2 Tips
> At least, test your power pin first. If having problem, refer to 'Appendix / Hardware Docs', and check the input/output voltage on related chip pins. 
> Buy a voltage-meter and don't cry. 
> Considering to use 6 pieces of Nanfu No.5 batteries (~9 Volt) to power up the Arduino board and motor-driving-board together. So far, power modules are separated. 

## 2017.02.22

### 1.1 Async-threads Communication:
> Threads can be run at background, so you can't expect them executed in sequence!!!  But according to your thread "run(self)" function, those logics are run sequencially!!!!!

### 1.2 Solution:
> Make sure your don't get lost in one previous loop, but actually you think you can update this variable, which related to jump out the loop in next sequencial function.

> Also, in mul-threads programming, the lock.acquire() and  lock.release() are PAIRED at any moment. Make sure you touch the shared variables with "lock".



##  2017.02.21

### 1.1 Communication Model:
>  PC <--> esp8266 (known as wifi module) <--> Arduino (Uart)

>  Usually, if we only use esp8266 to receive mesg but not feedback. If we want to feedback at same rate (50ms etc.), arduino's own Uart buffer would have conflicts whenwe try to read and write mesg at almost the same time.
>  Received mesg and mesg want to give back to PC would "interwined" in Arduino buffer. Especially when esp8266 module needs some delay (probablely 20~50ms) to between a "SEND" command and preping well for your input data. However, the best way to check if you need to consider this problem in fast communication rate is to open "Arduino's Serial Monitor" to have a close look on the buffer.

### 1.2 Solution:
>  Command sent-out rate from PC is set to ~200ms, and Arduino send a "Send" command to esp8266 at about first 50ms as soon as it recognizes the formatted command, and then write back the feedback info. Then it delay the rest of the time (for about 130ms), then check the buffer and see if there is any new command info. 
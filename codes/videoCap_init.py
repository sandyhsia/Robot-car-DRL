import numpy as np
import cv2


cap = cv2.VideoCapture(0)
#fourcc = cv2.VideoWriter_fourcc(*'XVID')
#out = cv2.VideoWriter('outout.avi',fourcc, 20.0, (640,480))


cap.set(3,1080)        ###wide
cap.set(4,720)         ###height


while(cap.isOpened()):
    ret, frame = cap.read()
    if ret==True:
       
        #out.write(frame)

        cv2.imshow('frame',frame)

        w = cap.get(3)
        print "w", w
        h = cap.get(4)
        print "h", h
        #print cap.get(CV_CAP_PROP_FRAME_HEIGHT)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

# Release everything if job is finished
cap.release()
#out.release()
cv2.destroyAllWindows()
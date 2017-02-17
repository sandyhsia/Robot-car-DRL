import cv2  
import numpy as np


# Read in
img = cv2.imread('11_2.jpg')

# Filter
# img = cv2.bilateralFilter(img, 9,75,75)
img = cv2.GaussianBlur(img, (3,3), 0)

# Convert2binary
gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 3, 5)
#adaptive_method = ADAPTIVE_THRESH_MEAN_C, threshold_type=THRESH_BINARY, block_size=3, param1=5

# edges = cv2.Canny(img, 20, 150, apertureSize = 3)
  

# FindContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  
edges, contours, hierarchy=cv2.findContours(binary,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)  

# show immediate canny image.
cv2.drawContours(img, contours,-1,(0,0,255),3)
cv2.imshow("img", img)  
cv2.imshow("edges", edges)
cv2.imwrite("edge.jpg", edges)
cv2.waitKey(200)


#print(hierarchy)

rectMax_area = 0
rectMax_num = 0

for i in range(0, len(contours)):
	cnt = contours[i]
	cntarea = cv2.contourArea(cnt, 0)
	if cntarea > 50 and cntarea < 30000:
		
		# If the contour is approx rectangle 
		# area = cv2.contourArea(cnt)
		x,y,w,h = cv2.boundingRect(cnt)
		rect_area = w*h
		extent = float(cntarea)/rect_area


		if extent >= 0.5:
			if cntarea > rectMax_area:
				rectMax_area = cntarea
				rectMax_num = i
			#cv2.drawContours(gray, contours, i,(255,0,0),3)

		cv2.imshow("result", gray) 
		cv2.waitKey(20)
		#print(j)


cv2.drawContours(gray, contours, rectMax_num,(128,0,0),3)
cv2.imshow("result", gray) 
cv2.waitKey(800)



# calulate mass center(cx, cy), rectangle center(x+w/2, y+h/2)
cnt = contours[rectMax_num]
M = cv2.moments(cnt)
#print M
cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
circle_center = (cx,cy)
print(circle_center)
cv2.circle(gray, circle_center, 2, (0,0,0),2)

'''
rect = cv2.minAreaRect(cnt)
(x,y),(w,h), angle = rect
#print(rect)
#print(angle)
box = cv2.boxPoints(rect)
box = np.int0(box)
gray = cv2.drawContours(gray,[box],0,(128,0,0),2)
rect_center = (x, y)
print(rect_center)
'''



#print(circle_center)
#print(rect_center)

#print(len(hierarchy))
#vector = hierarchy[:,0]
#print(vector[0])



'''
childNum = 0
larger_cx = 0
larger_cy = 0
largerRatio = 0
for i in range(0, len(contours)):
	vector = hierarchy[:,i]
	if vector[0,3] == rectMax_num:
		childNum=childNum+1
		print(vector)
		cnt = contours[vector[0,3]]
		outercntarea = cv2.contourArea(cnt)

		cnt = contours[vector[0,2]]
		innercntarea = cv2.contourArea(cnt)
		ratio = float(innercntarea/outercntarea)
		
		M = cv2.moments(cnt)
		#print M
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
		circle_center = (cx,cy)
		# print(circle_center)
		# cv2.circle(gray, circle_center, 2, (128,0,0),2)
		print(ratio)

		if ratio > largerRatio:
			largerRatio = ratio
			larger_cx = cx
			larger_cy = cy

	#if childNum == 2:
	#	break

print(childNum)
tanValue = (larger_cy - y)/(larger_cx - x)
actual_angle = np.arctan([tanValue])
print(actual_angle/3.14159*180)
circle_center = (larger_cx,larger_cy)
cv2.circle(gray, circle_center, 2, (128,0,0),29)
cv2.drawContours(gray, contours, rectMax_num,(128,0,0),3)
'''

###################################
#Matching Shape
###################################

cnt1 = contours[rectMax_num]
arearank = 0
larger_cx = 0
larger_cy = 0

for i in range(0, len(contours)):
	cnt2 = contours[i]
	cntarea = cv2.contourArea(cnt2, 0)
	if  cntarea > 50 and cv2.matchShapes(cnt1, cnt2, 1, 0.0) <= 0.01 and cntarea/cv2.contourArea(cnt1, 0) < 0.1:
		#print(i)
		#print(cv2.matchShapes(cnt1, cnt2, 1, 0.0))
		cv2.drawContours(gray, contours, i,(128,0,0),3)
		print(cntarea/cv2.contourArea(cnt1, 0))

		
		M = cv2.moments(cnt2)
		#print M
		new_x = int(M['m10']/M['m00'])
		new_y = int(M['m01']/M['m00'])
		circle_center = (new_x,new_y)


		#print(circle_center)
		cv2.circle(gray, circle_center, 2, (128,0,0),2)
		cv2.line(gray, (new_x, new_y), (cx, cy), (200, 0, 0), 2)
		cv2.imshow("result", gray) 
		#cv2.waitKey(80)
		tanValue = (new_y - cy)/(new_x - cx)
		print(tanValue)
		actual_angle = np.arctan([tanValue])
		print((actual_angle/3.1415926)*180)

		if cntarea>arearank :
			arearank = cntarea
			larger_cx = new_x
			larger_cy = new_y
'''
tanValue = (larger_cy - cy)/(larger_cx - cx)
actual_angle = np.arctan([tanValue])
turnangle=((actual_angle/3.1415926)*180)-135+90
print(turnangle)
cv2.line(gray, (cx+10*np.cos(turnangle*3.1415926/180), cy+10*np.sin(turnangle*3.1415926/180)), (cx, cy), (20, 0, 0), 4)
print((cx, cy))
print(cx+np.cos((turnangle/180)*3.1415926)*10)
cv2.circle(gray, ((larger_cx, larger_cy)), 2, (0,0,0),5)

'''

'''
rect = cv2.minAreaRect(cnt2)
(x,y),(w,h), angle = rect
print(rect)
print(angle)
# cv2.line(gray, (cx+np.cos(angle/180*3.1415926)*100, cx+np.sin(angle/180*3.1415926)*100), (cx, cy), (200, 0, 0), 2)
box = cv2.boxPoints(rect)
box = np.int0(box)
gray = cv2.drawContours(gray,[box],0,(0,0,0),20)
cv2.imshow("result", gray)
cv2.waitKey(800)
'''


cv2.imwrite("save.jpg", gray)


'''
pentagram = contours[7]
print(pentagram[1])
print(areai)


  
#leftmost = tuple(pentagram[:,0][pentagram[:,:,0].argmin()])  
#rightmost = tuple(pentagram[:,0][pentagram[:,:,0].argmax()])  
  
#cv2.circle(gray, leftmost, 2, (0,255,0),3)   
#cv2.circle(gray, rightmost, 2, (0,0,255),3)
#gray = cv2.rectangle(gray, leftmost, rightmost, (0,0,255))


x, y, w, h = cv2.boundingRect(pentagram)
cv2.rectangle(gray, (x, y), (x+w, y+h), (0, 0, 0), 2)
print(x)
print(y)
print(type(x))
retval, triangle = cv2.minEnclosingTriangle(pentagram)

cnt = contours[areai]
M = cv2.moments(cnt)
print M
cx = int(M['m10']/M['m00'])
cy = int(M['m01']/M['m00'])
print(cx)
print(cy)
circle_center = (cx,cy)
cv2.circle(gray, circle_center, 2, (0,0,0),3)

rect = cv2.minAreaRect(cnt)
(x,y),(w,h), angle = rect
print(rect)
print(angle)
box = cv2.boxPoints(rect)
box = np.int0(box)
gray = cv2.drawContours(gray,[box],0,(0,0,0),2)



cv2.imshow("result1", gray) 
cv2.waitKey(20000)


'''
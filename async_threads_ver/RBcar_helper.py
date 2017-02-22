#!/usr/bin/python
#
import sys
import time
import numpy as np
from helper_Feb16 import *

class RBcar:
    """Robot car
    """

    def __init__(self, car_center=(0,0), mark1_center=(0,0), mark2_center=(0,0), target_point=(0,0), is_arrival=0, command_to_give="q", current_speed=0.00, target_speed=0.00, diff_in_pixel=50.00, diff_in_angle=30.00):
        self.car_center = car_center
        self.mark1_center = mark1_center
        self.mark2_center = mark2_center

        self.target_point = target_point
        self.is_arrival = is_arrival
        self.command_to_give = command_to_give
        self.current_speed = current_speed
        self.target_speed = target_speed
        self.diff_in_pixel = diff_in_pixel
        self.diff_in_angle = diff_in_angle
        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.car_center_backup = (0,0)
        self.mark1_center_backup = (0,0)
        self.mark2_center_backup = (0,0)
        self.current_angle = 0.00
        self.current_angle_backup = 0.00
        self.target_angle = 0.00
        self.width = 0.00
        self.height = 0.00
        self.car_mark1_distance = 0.00
        self.car_mark2_distance = 0.00
        self.angle_error = 0.00
        self.speed_error = 0.00

    def check_and_try_restore(self):
        if ((abs(two_point_distance(self.car_center, self.mark1_center) - self.car_mark1_distance)) <= 10 and abs(two_point_distance(self.car_center, self.mark2_center) - self.car_mark1_distance) <= 10 ):
            return 1

        elif ((abs(two_point_distance(self.car_center, self.mark1_center) - self.car_mark1_distance)) > 10 and abs(two_point_distance(self.car_center, self.mark2_center) - self.car_mark1_distance) <= 10 ):
            angle2_in_degree = vector_direction(car_center, mark2_center)
            angle1_in_degree = angle2_in_degree + 90

            if(angle1_in_degree > 180):
                angle1_in_degree -= 360

            self.mark1_center = (car_center[0]+car_mark1_distance*np.cos(angle1_in_degree), car_center[1]-car_mark1_distance*np.sin(angle1_in_degree))
            return 2

        elif ((abs(two_point_distance(self.car_center, self.mark1_center) - self.car_mark1_distance)) <= 10 and abs(two_point_distance(self.car_center, self.mark2_center) - self.car_mark1_distance) > 10 ):
            angle1_in_degree = vector_direction(car_center, mark1_center)
            angle2_in_degree = angle2_in_degree - 90

            if(angle1_in_degree > 180):
                angle1_in_degree += 360

            self.mark2_center = (car_center[0]+car_mark2_distance*np.cos(angle2_in_degree), car_center[1]-car_mark2_distance*np.sin(angle2_in_degree))
            return 3

        else:
        	self.restore_backup()
        	return 4


    def update(self, current_speed):
        """
        Based on current car_center, mark1_center, mark2_center
        calculate:
            distance_to_target_point;
            current_angle;
            angle_error;
            command_to_give;
            target_speed;
            #######
            target_speed calculation should be related to PID...
        """
        
        self.current_speed = current_speed
        self.current_angle = self.car_angle_deter(self.car_center, self.mark1_center, self.mark2_center)
        self.target_angle = vector_direction(self.car_center, self.target_point)
        self.angle_error = self.current_angle - self.target_angle ### !!! need checking again, who minus who.

        if(self.check_Arrial() == 1):
            self.command_to_give = "q"
            return 1

        else:
            self.command_to_give = self.command_calculator(self.target_angle, self.current_angle)####################################################################################!!!!!
            return 2 ### return value? 1 too???


    def set_CarCenter(self, car_center):
        """If difference in backup point and setting point is too large, ie larger than diff_in_pixel, then return 0 as setting failure
           Else return 1 as setting success 
           #############
           May need judgement on car_center format
        """

        if(two_point_distance(self.car_center, self.car_center_backup) > self.diff_in_pixel):
            return 0
        else: 
            self.car_center_backup = self.car_center
            self.car_center = car_center
            return 

    def set_Mark1Center(self, mark1_center):
        """If difference in backup point and setting point is too large, ie larger than diff_in_pixel, then return 0 as setting failure
           Else return 1 as setting success 
           #############
           May need judgement on mark1_center format
        """

        if(two_point_distance(self.mark1_center, self.mark1_center_backup) > self.diff_in_pixel):
            return 0
        else: 
            self.mark1_center_backup = self.mark1_center
            self.makr1_center = mark1_center
            return 1

    def set_Mark2Center(self, mark2_center):
        """If difference in backup point and setting point is too large, ie larger than diff_in_pixel, then return 0 as setting failure
           Else return 1 as setting success 
           #############
           May need judgement on mark2_center format
        """

        if(two_point_distance(self.mark2_center, self.mark2_center_backup) > self.diff_in_pixel):
            return 0
        else: 
            self.mark2_center_backup = self.mark2_center
            self.makr2_center = mark2_center
            return 1

    def set_CurrentAngle(self, angle):
        """If difference in backup angle and setting angle is too large, ie larger than diff_in_angle, then return 0 as setting failure
           Else return 1 as setting success 
           #############
           May need judgement on angle format/range
        """

        if(abs(self.current_angle - angle) > self.diff_in_angle):
            return 0
        else: 
            self.current_angle_backup = self.current_angle
            self.current_angle = angle
            return 1

    def set_TargetPoint(self, target_point):
        """Setting a new target point.
           If is_arrival == 0, then return 0 as setting failure
           Else return 1 as setting success 
           #############
           May need judgement on target_point format
        """

        if(self.is_arrival != 1):
            return 0
        else: 
            self.target_point = self.target_point
            self.is_arrival = 0
            return 1

    def check_Arrial(self):
        distance_error = two_point_distance(self.car_center, self.target_point)
        
        if(distance_error < w or distance_error < d):
            self.is_arrival = 1

        else: 
            self.is_arrival = 0

            return self.is_arrival
	  
    def car_angle_deter(self, car_center, mark1_center, mark2_center):
        default_direction = 90 #unit:degree
        angle1_in_degree = vector_direction(car_center, mark1_center)
        angle2_in_degree = vector_direction(car_center, mark2_center)


        if angle1_in_degree <=0 and angle2_in_degree >=0:
            car_CurrentAngle = 180 + (angle1_in_degree + angle2_in_degree)*0.5

        else:
            car_CurrentAngle = (angle1_in_degree + angle2_in_degree)*0.5

        
        return car_CurrentAngle

    def restore_backup(self):   
        self.car_center = self.car_center_backup
        self.mark1_center = self.mark1_center_backup
        self.mark2_center = self.mark2_center_backup

    def full_backup(self):
        self.car_center_backup = self.car_center
        self.mark1_center_backup = self.mark1_center
        self.mark2_center_backup = self.mark2_center
        
    def command_calculator(target_direction, current_direction, angle_param):
        command = 'q'
        
        if (target_direction - current_direction <= angle_param and target_direction - current_direction >=0) or (target_direction - current_direction >= (-angle_param) and target_direction - current_direction <= 0):
            command = 'w' ## forward

        elif (target_direction - current_direction > angle_param and target_direction - current_direction <=  180 - angle_param):
            command = 'a' 

        elif target_direction - current_direction < (-angle_param) and target_direction - current_direction >=  -(180 - angle_param):
            command = 'd'

        else:
            command = 'a' ## backward

        return command
#!/usr/bin/python
#
import sys
import time

class PID:
    """PID Controller
    """

    def __init__(self, P=0.2, I=0.0, D=0.0, prop_sample_time=0.00, int_sample_time=0.00, deri_sample_time=0.00):

        self.Kp = P
        self.Ki = I
        self.Kd = D

        self.prop_sample_time = prop_sample_time
        self.int_sample_time = int_sample_time
        self.deri_sample_time = deri_sample_time
        self.current_time = time.time()
        self.last_time = self.current_time
        self.last_integral_time = self.current_time
        self.last_derivative_time = self.current_time

        self.clear()

    def clear(self):
        """Clears PID computations and coefficients"""
        self.SetPoint = 0.0

        self.PTerm = 0.0
        self.ITerm = 0.0
        self.DTerm = 0.0
        self.last_error = 0.0

        # Windup Guard
        self.windup_guard = 20.0

        self.output = 0.0

    def update(self, feedback_value):
        """Calculates PID value for given reference feedback
        .. math::
            u(t) = K_p e(t) + K_i \int_{0}^{t} e(t)dt + K_d {de}/{dt}
        """
        error = -self.CurrentPoint + feedback_value 
        # feedback_value is actually the value you want.
        # self.CurrentPoint is actually the current value.

        self.current_time = time.time()
        delta_time = self.current_time - self.last_time
        delta_error = error - self.last_error

        if (delta_time >= self.prop_sample_time):
            self.PTerm = self.Kp * error
            self.ITerm += error * delta_time

            if (self.ITerm < -self.windup_guard):
                self.ITerm = -self.windup_guard
            elif (self.ITerm > self.windup_guard):
                self.ITerm = self.windup_guard

            self.DTerm = 0.0
            if delta_time > 0:
                self.DTerm = delta_error / delta_time

            self.output = self.PTerm

            # Remember last time and last error for next calculation
            self.last_time = self.current_time
            self.last_error = error

        if self.current_time - self.last_integral_time >= self.int_sample_time:
            self.output += (self.Ki * self.ITerm)
            self.ITerm = 0
            self.last_integral_time = self.current_time

        if self.current_time - self.last_derivative_time >= self.deri_sample_time:
            self.output += self.Kd * self.DTerm
            self.DTerm = 0
            self.last_derivative_time = self.current_time

        if (delta_time >= self.prop_sample_time):
            self.CurrentPoint += self.output



    def setKp(self, proportional_gain):
        """Determines how aggressively the PID reacts to the current error with setting Proportional Gain"""
        self.Kp = proportional_gain

    def setKi(self, integral_gain):
        """Determines how aggressively the PID reacts to the current error with setting Integral Gain"""
        self.Ki = integral_gain

    def setKd(self, derivative_gain):
        """Determines how aggressively the PID reacts to the current error with setting Derivative Gain"""
        self.Kd = derivative_gain

    def setWindup(self, windup):
        """Integral windup, also known as integrator windup or reset windup,
        refers to the situation in a PID feedback controller where
        a large change in setpoint occurs (say a positive change)
        and the integral terms accumulates a significant error
        during the rise (windup), thus overshooting and continuing
        to increase as this accumulated error is unwound
        (offset by errors in the other direction).
        The specific problem is the excess overshooting.
        """
        self.windup_guard = windup

    def setPropotionalSampleTime(self, proportional_sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.prop_sample_time = proportional_sample_time

    def setIntegralSampleTime(self, integral_sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.int_sample_time = integral_sample_time

    def setDerivativeSampleTime(self, derivative_sample_time):
        """PID that should be updated at a regular interval.
        Based on a pre-determined sampe time, the PID decides if it should compute or return immediately.
        """
        self.deri_sample_time = derivative_sample_time

    def setCurrentPoint(self, current_value):
        """PID that should be updated to know the current state.
        """
        self.CurrentPoint = current_value
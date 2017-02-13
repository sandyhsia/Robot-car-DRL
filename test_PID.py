#!/bin/env python

from PID_helper import *
import time
import matplotlib.pyplot as plt

record_time = []
current_value = []

init_value = 12
test = PID(0.6, 0.1, 0.001, 0.2, 0, 10)
test.clear()
test.setCurrentPoint(init_value)
test.setPropotionalSampleTime(0.2)
test.setIntegralSampleTime(1)
test.setDerivativeSampleTime(1)
test.update(20)
print test.Kp
print test.output

for i in range(0,40):
    time.sleep(0.05)
    test.update(20)
    print "current_point", test.CurrentPoint
    print "P:", test.PTerm
    print "I:", test.ITerm
    print "D:", test.DTerm
    print "output:", test.output
    print ""
    record_time.append(test.current_time)
    current_value.append(test.CurrentPoint)

print "prop_sample_time", test.prop_sample_time
print "int_sample_time", test.int_sample_time
print "deri_sample_time", test.deri_sample_time
plt.plot(record_time, current_value)
plt.show()
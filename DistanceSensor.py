#!/usr/bin/env python

import threading
import time
import random

from Globals import Globals
from Observable import Observable

try:
    import wiringpi
except ImportError:
    print "wiringpi not found, switching to simulation"
    Globals.globSimulate = True


GPIO_INPUT = 0
GPIO_OUTPUT = 1
GPIO_PWM = 2

UPDATEINTERVAL = 0.5 # seconds. Must be >= 0.3s!!
MAXVALUES = 7

class DistanceSensor(threading.Thread, Observable):
    keepRunning = True
    lastValue = -1
    values = []
    pinTrigger = -1
    pinEcho = -1
    medianRange = 5

    def __init__(self, pt, pe):
        threading.Thread.__init__(self)
        Observable.__init__(self)
        self.pinTrigger = pt
        self.pinEcho = pe

        if not Globals.globSimulate:
	    wiringpi.pinMode(self.pinTrigger, GPIO_OUTPUT)
	    wiringpi.pinMode(self.pinEcho, GPIO_INPUT)

    def updateValue(self):
	if Globals.globSimulate:
	    val = (self.values[-1][1] if len(self.values) > 0 else 0) + random.randint(-10, 10)
	else:
	    # Send 10us pulse to trigger
	    wiringpi.digitalWrite(self.pinTrigger, 1)
	    time.sleep(0.00001)
	    wiringpi.digitalWrite(self.pinTrigger, 0)
	    start = time.time()

	    while wiringpi.digitalRead(self.pinEcho)==0:
	      start = time.time()

	    while wiringpi.digitalRead(self.pinEcho)==1:
	      stop = time.time()

	    # Calculate pulse length
	    elapsed = stop-start

	    # Distance pulse travelled in that time is time
	    # multiplied by the speed of sound (cm/s)
	    distance = elapsed * 34300

	    # That was the distance there and back so halve the value
	    val = distance / 2


	if val < 0:
	    val = 0

	currtime = int(time.time() * 1000) # this is milliseconds so JavaScript doesn't have to do this
	self.values.append([currtime, val])
	self.values = self.values[-MAXVALUES:]
	self.emit("DistanceSensor", self)

    def getCurrentDistance(self):
	if len(self.values) == 0:
	    return -1

	window = [d[1] for d in self.values[-self.medianRange:]]
	s = len(window)
	window.sort()
	return window[s/2] if s % 2 == 1 else (window[s/2] + window[s/2 - 1])/2.0

    def getDistanceHistory(self):
	return self.values

    def setMedianRange(self, val):
	self.medianRange = max(1, val)

    def shutdown(self):
    	self.keepRunning = False

    def run(self):
    	while self.keepRunning:
	    if not Globals.globSimulate:
		wiringpi.digitalWrite(self.pinTrigger, 0)

	    self.updateValue()

	    if not Globals.globSimulate:
		wiringpi.digitalWrite(self.pinTrigger, 0)

            # Allow module to settle
	    time.sleep(UPDATEINTERVAL)

if __name__ == '__main__':
    # Set pins as output and input
    Globals.globSimulate = True
    if not Globals.globSimulate:
	wiringpi.wiringPiSetupGpio()

    delay = 0.1
    ds = DistanceSensor(1, 2)
    ds.start()

    for i in range(0, 10):
        print ds.getCurrentDistance()
        time.sleep(0.2)

    ds.shutdown()
    ds.join()


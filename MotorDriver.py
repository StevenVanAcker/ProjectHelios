#!/usr/bin/env python

import threading
import time
from Globals import Globals
from Observable import Observable

try:
    import wiringpi
except:
    print "wiringpi not found, switching to simulation"
    Globals.globSimulate = True

# Don't touch these
LEFT_L  = 0
LEFT_R  = 1
RIGHT_L = 2
RIGHT_R = 3
VERT_L  = 4
VERT_R  = 5

GPIO_INPUT = 0
GPIO_OUTPUT = 1
GPIO_PWM = 2

UPDATEINTERVAL = 0.01 # seconds
MAXIDLE = 0.3 # seconds

class MotorDriver(threading.Thread, Observable):
    keepRunning = True
    pwmValue = 700
    lastHorizontalChange = 0
    lastVerticalChange = 0
    debug = False
    singleSteerMode = False

    # left, right, vert motors
    motorPins = []
    pinValues = [False] * 6

    def __init__(self, pins):
        threading.Thread.__init__(self)
        Observable.__init__(self)
    	if len(pins) != 6:
	    raise "MotorDriver needs 6 pins"

	self.motorPins = pins

	if not Globals.globSimulate:
	    for pn in range(0, 6):
		pin = self.motorPins[pn]
		wiringpi.pinMode(pin, GPIO_OUTPUT)
	    wiringpi.pinMode(18, GPIO_PWM)
	    wiringpi.pwmWrite(18, self.pwmValue)

    def sendToRPi(self):
        for pn in range(0, 6):
            pin = self.motorPins[pn]
            val = self.pinValues[pn]
	    if not Globals.globSimulate:
		wiringpi.digitalWrite(pin, 1 if val else 0)

	if not Globals.globSimulate:
	    wiringpi.pwmWrite(18, self.pwmValue)
	
	if self.debug:
	    print "Sent to RPi: pinValues(%s) pwmValue(%s)" % (self.pinValues, self.pwmValue)

    def setPin(self, pinName, val):
	self.pinValues[pinName] = val
	now = time.time()

	if pinName == VERT_L or pinName == VERT_R:
	    self.lastVerticalChange = now
	else:
	    self.lastHorizontalChange = now

	self.emit("MotorDriver", self)


    def setSpeed(self, val):
    	self.pwmValue = max(min(val, 1023), 0)
	self.emit("MotorDriver", self)

    def setSingleSteerMode(self, val):
    	self.singleSteerMode = val
	self.emit("MotorDriver", self)

    def getSingleSteerMode(self):
    	return self.singleSteerMode

    def statusByPin(self, l, r):
        if self.pinValues[l] == self.pinValues[r]:
	    return "stop"
	if self.pinValues[l]: 
	    return "backward"
	return "forward"
    def statusLeft(self):
        return self.statusByPin(LEFT_L, LEFT_R)
    def statusRight(self):
        return self.statusByPin(RIGHT_L, RIGHT_R)
    def statusVert(self):
        return self.statusByPin(VERT_L, VERT_R)
    def getPWM(self):
    	return self.pwmValue

    def _leftForward(self):
    	self.setPin(LEFT_L, False) ; self.setPin(LEFT_R, True)
    def _leftBackward(self):
    	self.setPin(LEFT_R, False) ; self.setPin(LEFT_L, True)
    def _leftStop(self):
    	self.setPin(LEFT_R, False) ; self.setPin(LEFT_L, False)

    def _rightForward(self):
    	self.setPin(RIGHT_L, False) ; self.setPin(RIGHT_R, True)
    def _rightBackward(self):
    	self.setPin(RIGHT_R, False) ; self.setPin(RIGHT_L, True)
    def _rightStop(self):
    	self.setPin(RIGHT_R, False) ; self.setPin(RIGHT_L, False)

    def _vertForward(self):
    	self.setPin(VERT_L, False) ; self.setPin(VERT_R, True)
    def _vertBackward(self):
    	self.setPin(VERT_R, False) ; self.setPin(VERT_L, True)
    def _vertStop(self):
    	self.setPin(VERT_R, False) ; self.setPin(VERT_L, False)


    def turnLeft(self):
	self._rightForward()
	if not self.singleSteerMode:
		self._leftBackward()
    def turnRight(self):
	self._leftForward()
	if not self.singleSteerMode:
	    self._rightBackward()
    def forward(self):
	self._leftForward() ; self._rightForward()
    def backward(self):
	self._leftBackward() ; self._rightBackward()
    def up(self):
	self._vertForward()
    def down(self):
	self._vertBackward()

    def increasePWM(self, d = 20):
    	self.setSpeed(self.pwmValue + d)

    def decreasePWM(self, d = 20):
    	self.setSpeed(self.pwmValue - d)

    def stop(self):
    	self.stopVertical()
    	self.stopHorizontal()
    def stopVertical(self):
	self._vertStop()
    def stopHorizontal(self):
	self._leftStop()
	self._rightStop()

    def shutdown(self):
    	self.keepRunning = False
    	self.stop()
	self.sendToRPi()

    def run(self):
    	while self.keepRunning:
	    now = time.time()
	    if self.lastVerticalChange + MAXIDLE < now:
	    	self.stopVertical()

	    if self.lastHorizontalChange + MAXIDLE < now:
	    	self.stopHorizontal()

	    self.sendToRPi()
	    time.sleep(UPDATEINTERVAL)

if __name__ == '__main__':
    Globals.globSimulate = True
    delay = 0.1
    md = MotorDriver([1,2,3,4,5,6]) #Fake values
    md.debug = True
    md.start()
    md.turnLeft() ; time.sleep(delay)
    md.turnRight() ; time.sleep(delay)
    md.forward() ; time.sleep(delay)
    md.backward() ; time.sleep(delay)
    md.up() ; time.sleep(delay)
    md.down() ; time.sleep(delay)
    md.stop() ; time.sleep(delay)
    md.shutdown()
    md.join()


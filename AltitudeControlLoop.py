#!/usr/bin/env python

import curses, time, sys
from curses import wrapper
from DistanceSensor import DistanceSensor
from MotorDriver import MotorDriver
from Observable import Observable

class AltitudeControlLoop(Observable):
    motorDriver = None
    distanceSensor = None
    height = 0
    auto = False
    forceDescent = True
    debug = False

    def __init__(self, md, ds):
    	Observable.__init__(self)
        self.motorDriver = md
	self.distanceSensor = ds
	self.distanceSensor.subscribe(self.update)

    def setHeight(self, val):
        self.height = val
	self.emit("AltitudeControlLoop", self)

    def keepThisHeight(self):
	self.setHeight(self.distanceSensor.getCurrentDistance())
	self.setAuto(True)

    def setAuto(self, val):
        self.auto = val
	self.emit("AltitudeControlLoop", self)

    def getAuto(self):
        return self.auto

    def setForceDescent(self, val):
        self.forceDescent = val
	self.emit("AltitudeControlLoop", self)

    def getForceDescent(self):
        return self.forceDescent

    def getHeight(self):
        return self.height

    def update(self, etype, src):
	if self.auto and etype == "DistanceSensor":
	    alt = src.getCurrentDistance()
	    diff = alt - self.height
	    if self.debug:
		print "Alt: %f, Height: %f, Diff: %f" % (alt, self.height, diff)

	    if self.forceDescent and diff > 5:
		return self.motorDriver.down()
	    if diff < -5:
	        return self.motorDriver.up()
	    
	    self.motorDriver.stopVertical()

if __name__ == '__main__':
    md = MotorDriver([1,2,3,4,5,6])
    ds = DistanceSensor(7,8)
    acl = AltitudeControlLoop(md, ds)
    acl.debug = True
    ds.lastValue = 100
    md.start()
    ds.start()
    acl.keepThisHeight()

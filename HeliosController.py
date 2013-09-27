#!/usr/bin/env python

import time, sys
from ConfigParser import ConfigParser
from Globals import Globals

try:
    import wiringpi
except:
    print "wiringpi not found, switching to simulation"
    Globals.globSimulate = True

from MotorDriver import MotorDriver
from DistanceSensor import DistanceSensor
from AltitudeControlLoop import AltitudeControlLoop
from Camera import Camera
from Observable import Observable
from subprocess import call


class HeliosController(Observable):
    md = None
    ds = None
    acl = None
    cam = None
    status = {}

    def __init__(self, conffile):
        Observable.__init__(self)
	cp = ConfigParser()
	cp.read(conffile)

	if not Globals.globSimulate:
	    wiringpi.wiringPiSetupGpio()

	self.md = MotorDriver([
		    cp.getint("MotorDriver", "LEFT_L"),
		    cp.getint("MotorDriver", "LEFT_R"),
		    cp.getint("MotorDriver", "RIGHT_L"),
		    cp.getint("MotorDriver", "RIGHT_R"),
		    cp.getint("MotorDriver", "VERTICAL_L"),
		    cp.getint("MotorDriver", "VERTICAL_R"),
		    ])
	self.md.start()

	self.ds = DistanceSensor(
		    cp.getint("DistanceSensor", "TRIGGER"),
		    cp.getint("DistanceSensor", "ECHO")
		    )
	self.ds.start()

	self.acl = AltitudeControlLoop(self.md, self.ds)

	self.update("MotorDriver", self.md)
	self.update("DistanceSensor", self.ds)
	self.update("AltitudeControlLoop", self.acl)

	self.md.subscribe(self.update)
	self.ds.subscribe(self.update)
	self.acl.subscribe(self.update)

	#self.setCamera(True)
	#self.acl.debug = True
	#self.md.debug = True

    def shutdown(self):
	self.md.shutdown()
	self.md.join()
	self.ds.shutdown()
	self.ds.join()
	self.setCamera(False)

    def turnLeft(self):
        self.md.turnLeft()
    def turnRight(self):
        self.md.turnRight()

    def forward(self):
        self.md.forward()
    def backward(self):
        self.md.backward()
    def up(self):
        self.md.up()
    def down(self):
        self.md.down()

    def setSpeed(self, val):
    	self.md.setSpeed(val)
    def setAuto(self, val):
    	self.acl.setAuto(val)
    def setHeight(self, val):
    	self.acl.setHeight(val)
    def setForceDescent(self, val):
        self.acl.setForceDescent(val)
    def setSingleSteerMode(self, val):
    	self.md.setSingleSteerMode(val)

    def setCamera(self, val):
	if self.cam == None:
	    if val:
		print "HeliosController enabling camera"
		self.cam = Camera()
		self.cam.start()
	    else:
		print "HeliosController tried to disable camera, but is not active"
	else:
	    if val:
		print "HeliosController tried to enable camera, but is already active"
	    else:
		print "HeliosController disabling camera"
		self.cam.shutdown()
		self.cam.join()
		self.cam = None

    def getImage(self):
	if self.cam != None:
	    return self.cam.getImage()
	return None


    def update(self, etype, src):
	if etype == "MotorDriver":
	    self.status["statLeft"] = src.statusLeft()
	    self.status["statRight"] = src.statusRight()
	    self.status["statVert"] = src.statusVert()
	    self.status["pwmValue"] = src.getPWM()
	    self.status["singleSteeringMode"] = src.getSingleSteerMode()

	if etype == "DistanceSensor":
	    self.status["currentAltitude"] = src.getCurrentDistance()
	    self.status["altitudeHistory"] = src.getDistanceHistory()

	if etype == "AltitudeControlLoop":
	    self.status["requestedAltitude"] = src.getHeight()
	    self.status["maintainAltitude"] = src.getAuto()
	    self.status["forceDescent"] = src.getForceDescent()

	self.emit("HeliosController", self)

    def getStatus(self):
        return self.status

if __name__ == '__main__':
    hc = HeliosController("config.ini")
    time.sleep(5)
    hc.shutdown()


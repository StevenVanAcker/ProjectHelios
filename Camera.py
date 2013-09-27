#!/usr/bin/env python

from threading import Thread, Lock
from Observable import Observable
from subprocess import Popen, PIPE
from Globals import Globals

import time

class Camera(Observable, Thread):
    keepRunning = True
    cmd = ["raspistill","-o","-","-e","jpg","-t","999999999","-n","-tl","100","-w","400","-h","300","-q","80"]
    lastImage = None
    imgLock = Lock()

    def __init__(self):
        Observable.__init__(self)
        Thread.__init__(self)
	if Globals.globFakeCamera:
	    self.cmd = ["./fakecam.py", "fakecam.mjpg"]

    def getImage(self):
	with self.imgLock:	
	    return self.lastImage

    def run(self):
        proc = Popen(self.cmd, stdout=PIPE)
	buffer = ""
	header = None

	f = proc.stdout

        while self.keepRunning:
	    data = f.read(1024)
	    if len(data) <= 0:
		self.keepRunning = False
		break

	    buffer += data

	    # search for the header
	    if header == None:
		if len(buffer) >= 10:
		    header = buffer[:10]
	    else:
		i = buffer.find(header, 1) # start at location 1...
		if i >= 0:
		    with self.imgLock:
			self.lastImage = buffer[:i]
		    buffer = buffer[i:]
		    if Globals.globFakeCamera:
			time.sleep(0.1)
		    self.emit("Camera", self)

    def shutdown(self):
        self.keepRunning = False

if __name__ == '__main__':

    def report(id, obj):
	print "Received image"

    c = Camera()
    c.subscribe(report)
    c.start()


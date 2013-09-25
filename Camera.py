#!/usr/bin/env python

from threading import Thread, Lock
from Observable import Observable
from subprocess import Popen, PIPE

class Camera(Observable, Thread):
    keepRunning = True
    cmd = []
    lastImage = None
    imgLock = Lock()

    def __init__(self, cmd = ["./fakecam.py", "nocam.jpg"]):
        Observable.__init__(self)
        Thread.__init__(self)
	self.cmd = cmd

    def getImage(self):
	with self.imgLock:	
	    return self.lastImage

    def run(self):
        proc = Popen(self.cmd, stdout=PIPE)
	buffer = ""
	header = None

	f = proc.stdout

        while self.keepRunning:
	    data = f.read(1024000)
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
		    self.emit("Camera", self)

    def shutdown(self):
        self.keepRunning = False

if __name__ == '__main__':

    def report(id, obj):
	print "Received image"

    c = Camera()
    c.subscribe(report)
    c.start()


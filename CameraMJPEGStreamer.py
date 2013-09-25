#!/usr/bin/env python

import sys
import subprocess
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import re

from Observable import Observable
from threading import Condition
from Camera import Camera

class CameraStore(object):
    camera = None
    image = None
    newImage = False
    C = Condition()

    def __init__(self, cam):
        camera = cam
	camera.subscribe(self.putImage)

    def putImage(self, id, cam):
	self.C.acquire()
	self.image = cam.getImage()
	self.newImage = True
	self.C.notify()
	self.C.release()
        

    def getImage(self):
        # wait until new image is available
	self.C.acquire()
	while not self.newImage:
	    self.C.wait()

	# make a copy of this image and indicate that we've seen this one
	imgCopy = self.image
	self.newImage = False
	self.C.release()
	return imgCopy


class CameraMJPEGStreamHandler(ThreadingMixIn, BaseHTTPRequestHandler):
    def do_GET(self):
        try:
	    self.send_response(200)
	    self.wfile.write("Content-Type: multipart/x-mixed-replace; boundary=--aaboundary")
	    self.wfile.write("\r\n\r\n")

	    while True:
	    	img = self.server.cameraStore.getImage()
		self.wfile.write("--aaboundary\r\n")
		self.wfile.write("Content-Type: image/jpeg\r\n")
		self.wfile.write("Content-length: "+str(len(img))+"\r\n\r\n" )
		self.wfile.write(img)
		self.wfile.write("\r\n\r\n\r\n")
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

class CameraMJPEGStreamer(HTTPServer):
    cameraStore = None
    camera = None
    def __init__(self, *args, **kw):
            HTTPServer.__init__(self, *args, **kw)
	    self.camera = Camera()
	    self.camera.start()
	    self.cameraStore = CameraStore(self.camera)

def main():
    try:
        server = CameraMJPEGStreamer(('', 8080), CameraMJPEGStreamHandler)
        print 'started CameraMJPEGStreamer...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

def testmain():
    xxx = Camera()
    xxx.start()
    yyy = CameraStore(xxx)

    while True:
        i = yyy.getImage()
	print "YYY got image"

if __name__ == '__main__':
    main()
    #testmain()

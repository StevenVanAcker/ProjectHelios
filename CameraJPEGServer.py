#!/usr/bin/env python

import sys
import subprocess
import string,cgi,time
from os import curdir, sep
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
import re

from Observable import Observable
from Camera import Camera

class CameraJPEGServerHandler(ThreadingMixIn, BaseHTTPRequestHandler):
    def do_GET(self):
        try:
	    img = self.server.camera.getImage()
	    self.send_response(200)
	    self.send_header("Content-Type","image/jpeg")
	    self.end_headers()
	    self.wfile.write(img)
        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

class CameraJPEGServer(HTTPServer):
    cameraStore = None
    camera = None
    def __init__(self, *args, **kw):
            HTTPServer.__init__(self, *args, **kw)
	    #self.camera = Camera()
    	    self.camera = Camera(["./fakecam.py", "nocam.jpg"])
	    self.camera.start()

def main():
    try:
    	print "About to start CameraJPEGServer..."
        server = CameraJPEGServer(('', 8080), CameraJPEGServerHandler)
        print 'started CameraJPEGServer...'
        server.serve_forever()
    except KeyboardInterrupt:
        print '^C received, shutting down server'
        server.socket.close()

def testmain():
    xxx = Camera(["./fakecam.py", "nocam.jpg"])
    xxx.start()

    while True:
        i = yyy.getImage()
	print "YYY got image"

if __name__ == '__main__':
    main()
    #testmain()

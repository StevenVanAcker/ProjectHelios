#!/usr/bin/env python

import time, re, sys, os
import json
import BaseHTTPServer

from HeliosController import HeliosController
from SocketServer import ThreadingMixIn


HOST_NAME = '' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 8000 # Maybe set this to 9000.
FILEROOT = "./webfiles/"

class HeliosHTTPServer(ThreadingMixIn, BaseHTTPServer.HTTPServer):
    def __init__(self, *args, **kw):
        BaseHTTPServer.HTTPServer.__init__(self, *args, **kw)
        self.controller = HeliosController("config.ini")

class HeliosHTTP(BaseHTTPServer.BaseHTTPRequestHandler):
    handlers = {}

    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(self):
        """Respond to a GET request."""
	self.handlers = {
		"quit": 		self.handler_quit,
		"status": 		self.handler_status,
		"up": 			self.handler_up,
		"down": 		self.handler_down,
		"turnLeft": 		self.handler_turnLeft,
		"turnRight": 		self.handler_turnRight,
		"forward": 		self.handler_forward,
		"backward": 		self.handler_backward,
		"setSpeed":		self.handler_setSpeed,
		"setAuto": 		self.handler_setAuto,
		"setHeight": 		self.handler_setHeight,
		"setForceDescent": 	self.handler_setForceDescent,
		"setSingleSteerMode": 	self.handler_setSingleSteerMode,
	    }

	#print "Get request for %s" % self.path
	if self.path == "" or self.path == "/":
	    self.path = "/index.html"

	x = self.dispatch(self.path)

	if x:
	    self.send_response(200)
	    self.send_header("Content-type", "application/json")
	    self.end_headers()
	    self.wfile.write(json.dumps(x))
	else:
	    request = os.path.join(FILEROOT, self.path.lstrip("/"))
	    if request.startswith(FILEROOT):
		# Maybe in webroot
		if not os.path.exists(request):
		    self.send_response(404)
		    self.send_header("Content-type", "text/html")
		    self.end_headers()
		    self.wfile.write("<html><body>File not found</body></html>")
		else:
		    f = open(request, 'rb')
		    self.send_response(200)
		    self.send_header('Content-type', self.guessMime(request))
		    self.end_headers()
		    self.wfile.write(f.read())
		    f.close() 
	    else:
		    self.send_response(404)
		    self.send_header("Content-type", "text/html")
		    self.end_headers()
		    self.wfile.write("<html><body>HAX!!</body></html>")

    def guessMime(self, fn):
	if fn.endswith(".html"):
	    return "text/html"

	if fn.endswith(".css"):
	    return "text/css"

	if fn.endswith(".js"):
	    return "application/javascript"

	if fn.endswith(".jpg"):
	    return "image/jpeg"

	if fn.endswith(".png"):
	    return "image/png"

	return "application/octet-stream"

    def dispatch(self, request):
	parts = re.sub(r"/+", "/", request.strip("/")).split("/")

	# might be a command
	if len(parts) > 1 and parts[0] == "call" and parts[1] in self.handlers:
	    return self.handlers[parts[1]](parts)

	return None

    def handler_quit(self, parts):
	self.server.controller.shutdown()
	self.server.server_close()
	sys.exit(0)
	return "Quitting"

    def handler_status(self, parts):
	return self.server.controller.getStatus()

    def handler_up(self, parts):
	self.server.controller.up()
	return self.server.controller.getStatus()
    def handler_down(self, parts):
	self.server.controller.down()
	return self.server.controller.getStatus()
    def handler_turnLeft(self, parts):
	self.server.controller.turnLeft()
	return self.server.controller.getStatus()
    def handler_turnRight(self, parts):
	self.server.controller.turnRight()
	return self.server.controller.getStatus()
    def handler_forward(self, parts):
	self.server.controller.forward()
	return self.server.controller.getStatus()
    def handler_backward(self, parts):
	self.server.controller.backward()
	return self.server.controller.getStatus()

    def handler_setSpeed(self, parts):
	if len(parts) < 3:
	    raise "ERROR: need more data"
	self.server.controller.setSpeed(int(parts[2]))
	return self.server.controller.getStatus()

    def handler_setAuto(self, parts):
	if len(parts) < 3:
	    raise "ERROR: need more data"
	self.server.controller.setAuto(parts[2].lower() == "true")
	return self.server.controller.getStatus()

    def handler_setHeight(self, parts):
	if len(parts) < 3:
	    raise "ERROR: need more data"
	self.server.controller.setHeight(int(parts[2]))
	return self.server.controller.getStatus()

    def handler_setForceDescent(self, parts):
	if len(parts) < 3:
	    raise "ERROR: need more data"
	self.server.controller.setForceDescent(parts[2].lower() == "true")
	return self.server.controller.getStatus()

    def handler_setSingleSteerMode(self, parts):
	if len(parts) < 3:
	    raise "ERROR: need more data"
	self.server.controller.setSingleSteerMode(parts[2].lower() == "true")
	return self.server.controller.getStatus()




if __name__ == '__main__':
    server_class = HeliosHTTPServer #BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), HeliosHTTP)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.controller.shutdown()
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)

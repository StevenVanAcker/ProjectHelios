#!/usr/bin/env python

# This tool simulates the raspberry pi camera's raspistill tool in timelapse mode with -o -
# Given the output from raspistill -tl 100 -o -, this tool will replay that stream of
# images over and over on stdout

import sys, time

delay = 0.1 #s

buffer = ""
header = None

fn = sys.argv[1]
f = open(fn, "rb")

while True:
    data = f.read(1024000)
    if len(data) <= 0:
	sys.stdout.write(buffer)
	time.sleep(0.1)
	f.close()
	f = open(fn, "rb")

    buffer += data

    # search for the header
    if header == None:
    	if len(buffer) >= 10:
	    header = buffer[:10]
    else:
        i = buffer.find(header, 1) # start at location 1...
	if i >= 0:
	    img = buffer[:i]
	    buffer = buffer[i:]
	    sys.stdout.write(img)
	    time.sleep(delay)

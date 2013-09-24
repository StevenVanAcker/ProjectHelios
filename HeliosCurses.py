#!/usr/bin/env python

import curses, time, sys
from curses import wrapper
from HeliosController import HeliosController
from subprocess import call

class HeliosCurses():
    stdscr = None
    controller = None

    def __init__(self):
	scr = curses.initscr(); curses.noecho(); curses.cbreak();
	scr.keypad(1)
	scr.clear()
        self.stdscr = scr
	self.controller = HeliosController("config.ini")
	self.controller.subscribe(self.redraw)

    def redraw(self, etype, src):
	self.stdscr.refresh()
	status = src.getStatus()

	statLeft = status["statLeft"]
	statRight = status["statRight"]
	statVert = status["statVert"]
	pwmValue = status["pwmValue"]
	ssm = status["singleSteeringMode"]
	alt = status["currentAltitude"]
	ralt = status["requestedAltitude"]
	autoalt = status["maintainAltitude"]
	forcedescent = status["forceDescent"]

	suffix = ""
	if autoalt:
	    suffix = " - AUTO - requested %04.3fcm" % ralt
	self.stdscr.addstr(1, 0, "Altitude:            %04.3fcm%s" % (alt, suffix))
	self.stdscr.clrtoeol()
	self.stdscr.addstr(2, 0, "Forced auto-descent: %s" % forcedescent)
	self.stdscr.clrtoeol()
	self.stdscr.addstr(3, 0, "Steering mode:       %s" % ssm)
	self.stdscr.clrtoeol()
	self.stdscr.addstr(4, 0, "PWM Value:           %d / 1023" % pwmValue)
	self.stdscr.clrtoeol()

	guiopt = { 
		'L': statLeft == "forward", 
		'R': statRight == "forward", 
		'l': statLeft == "backward", 
		'r': statRight == "backward",
		'D': statVert == "backward", 
		'U': statVert == "forward",
		}
	self.showArrows(6, 4, "layout.txt", guiopt)
	self.showHelp(15, 0, "help.txt")

    def showArrows(self, y, x, fn, opt):
	dy = 0
	for rawline in open(fn).readlines():
	    line = rawline.rstrip()
	    dx = 0
	    for c in list(line):
		o = curses.A_REVERSE if (c in opt and opt[c]) else 0
		l = " " if (c == " " or (c in opt and opt[c])) else "."
		self.stdscr.addstr(y + dy, x + dx, l, o)
		dx += 1
	    dy += 1

    def showHelp(self, y, x, fn):
	dy = 0
	for rawline in open(fn).readlines():
	    line = rawline.rstrip()
	    self.stdscr.addstr(y + dy, x, line)
	    dy += 1

    def handleKey(self, c):
	if c == "q":
	    self.controller.shutdown()
	    curses.endwin()
	    sys.exit(0)

	if c == "KEY_UP":
	    self.controller.forward()
	if c == "KEY_DOWN":
	    self.controller.backward()
	if c == "KEY_LEFT":
	    self.controller.turnLeft()
	if c == "KEY_RIGHT":
	    self.controller.turnRight()

	if c == " ":
	    self.controller.up()
	    self.controller.setAuto(False)
	if c == "d":
	    self.controller.down()
	    self.controller.setAuto(False)

	if c == "m":
	    self.controller.setHeight(self.controller.getStatus()["currentAltitude"])
	    self.controller.setAuto(not self.controller.getStatus()["maintainAltitude"])
	if c == "f":
	    self.controller.setForceDescent(not self.controller.getStatus()["forceDescent"])
	if c == "s":
	    self.controller.setSingleSteerMode(not self.controller.getStatus()["singleSteeringMode"])

	if c == "+" or c == "=":
	    pwm = self.controller.getStatus()["pwmValue"]
	    self.controller.setSpeed(min(pwm + 20, 1023))
	if c == "-" or c == "_":
	    pwm = self.controller.getStatus()["pwmValue"]
	    self.controller.setSpeed(max(pwm - 20, 0))

	if c == "i":
	    #call(["/usr/bin/raspistill", "-n", "-o", "out.jpg", "-t", "100", "-w", "640", "-h", "480", "-e", "jpg"])
	    stdscr.addstr(0,0, "Saved image: %s" % "out.jpg")
	    # FIXME: increase image filename
        
    def start(self):
	while True:
	    c = self.stdscr.getkey()
	    self.handleKey(c)

if __name__ == '__main__':
    hc = HeliosCurses()
    hc.start()



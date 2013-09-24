#!/usr/bin/env python

from collections import defaultdict

class Observable(object):
  store = None

  def __init__(self):
      object.__init__(self)
      self.store = []

  def emit (self, *args):
      for subscriber in self.store:
          response = subscriber(*args)

  def subscribe (self, subscriber):
      self.store.append(subscriber)


if __name__ == '__main__':
    class ObserverTest (object):
      name = "NONE"

      def __init__ (self, name):
	  self.name = name

      def printIt (self, val):
	  print "Instance %s received %s" % (self.name, val)

    def printIt(val):
        print "Received %s" % val

    o = Observable()
    ot1 = ObserverTest("ot-1")
    ot2 = ObserverTest("ot-2")


    o.subscribe(printIt)
    o.subscribe(ot1.printIt)
    o.subscribe(ot2.printIt)
    o.emit("xyz")

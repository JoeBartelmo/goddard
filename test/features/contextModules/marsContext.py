"""
This file will strictly be used for communication between mars and the step definitions

It will be responsible for maintaining a threaded connection to mars
and piping information too and from mars.

"""
from marsThread import MarsThread
from Queue import Queue

class MarsTestbed(object):

    def __init__(self):
        self.queue = Queue()
        self.mars = None
    
    def startConnectionToMars(self, debugMode = False):
        self.mars = MarsThread('config.json', self.queue, debugMode)
        self.mars.start()

    def closeConnectionToMars(self, forceful = True):
        if forceful == True:
            self.mars.stop()
        else:
            self.mars.gracefulStop()

    def sendCommandToMars(self, command):
        self.queue.put(command)
 

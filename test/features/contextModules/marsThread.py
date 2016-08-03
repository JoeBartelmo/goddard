import threading
from multiprocessing import Process
import sys
from select import select
import os

#Add mars files
sys.path.insert(0, '../../mars')
import run as Mars
import time

"""
This is going to be a thread that manages a thread which
runs mars.

The reason we have two threads here is so we can interrupt
mars mid processing if need be.
"""
class MarsThread(threading.Thread):
    def __init__(self, configFile, queueIn, debugMode):
        super(MarsThread, self).__init__()
        self._stop = threading.Event()
        self._gracefulStop = threading.Event()
        self.config = configFile
        self.queueIn = queueIn
        self.debugMode = debugMode

    def run(self):
        #configuration file defined in local directory

        print os.getcwd()        
        with open(self.config) as f:
            configs = f.read().splitlines()
        configString =""
        for i in configs:
            configString = configString + i
        json_string = configString.replace(" ", "")
        
        mars = Process(target=Mars.run, args=(json_string, self.queueIn, self.debugMode))
        mars.start()

        while self.stopped() == False and self.gracefulStopped() == False:
            time.sleep(3)
        
        if self.stopped():
            mars.terminate()
        else:
            self.queueIn.put('exit')
            mars.join()
        print 'Mars Thread Stopped'

    def stop(self, force = True):
        if force:
            self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

    def gracefulStopped(self):
        return self._gracefulStop.isSet()


# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import threading
import socket
import logging
import time
from constants import *

logger = logging.getLogger('mars_logging') 

class ThreadManager(threading.Thread):
    def __init__(self, threads, gui = None):
        '''
        Each thread should be a thread with a stop() and stopped() and isInit()
        '''
        super(ThreadManager, self).__init__()
        self._stop = threading.Event()
        self._threads = threads
        self._gui = gui

    def startThreadsSync(self):
        for i in range(0, len(self._threads)):
            if not self._threads[i].is_alive():
                self._threads[i].start()
        logger.info('Waiting for all threads to finish initilization...')
        #Gives threads time to determien whether or not they have started, or cant start
        for i in range(0, len(self._threads)):
            while not self._threads[i].isInit() and not self._threads[i].stopped():
                time.sleep(0.1)
            if self._threads[i].stopped():
                return False
        logger.info('Client Socket-Binding Threads Initialized!')
        return True

    def startInterface(self, guiOutput, cliMode = False):
        if cliMode:
            while True:
                time.sleep(0.5)
                command = raw_input('Type Your Command:')
                guiOutput.put(command)
                if command == MARS_KILL_COMMAND:
                    break 
        else:
            self._gui.start()

    def run(self):
        '''
        Launch each thread and keep track of whether or not thy are stopped
        If one is stopped, signal to close the other threads.
        '''
        logger.warning('Launching socket manager...')
        while self.stopped() != True:
            for i in range(0, len(self._threads)):
                if self._threads[i].stopped() == True:
                    logger.error('Detected a thread stopped')
                    self.stop()
                    break
                time.sleep(1)
        logger.warning('Stopping all Threads.')
        if self._gui is not None:
            self._gui.destroyEvent.set()
        for i in range(0, len(self._threads)):
            if self._threads[i].is_alive() and self._threads[i].isInit():
                self._threads[i].stop()
                self._threads[i].join()

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()

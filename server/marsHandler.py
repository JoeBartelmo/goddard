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
import sys
import logging
from select import select
sys.path.insert(0, '../mars')
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console

MARS_EXIT_COMMAND = 'exit'

class MarsThread(threading.Thread):
    '''
    The idea here is that the client will connect
    And we want to keep mars chugging when the client losses connection.
    We want to easily reconnnect, so we stick with queues here, mars won't stop
    until mars is explicitly stopped or watchdog stop is triggered
    '''
    def __init__(self, configuration, marsCommandQueue, marsConnectionQueue, marsOnlineQueue, debugEnabled = False):
        super(MarsThread, self).__init__()
        self._stop = threading.Event()

        self.config = configuration
        self.marsCommandQueue = marsCommandQueue
        self.marsConnectionQueue = marsConnectionQueue
        self.marsOnlineQueue = marsOnlineQueue
        self.debugEnabled = debugEnabled

    def run(self):
        Mars.run(self.config, self.marsCommandQueue, self.marsConnectionQueue, self.marsOnlineQueue, self.debugEnabled)
        '''
        Here we are on death. Usually Because mars quit, we would expect all logging to stop,
        but it persists because we still have the server up.
        To prevent logging handlers from just getting indefinitely larger, we remove them all on quit of mars
        '''
        debugLog = logging.getLogger('mars_logging')
        telemetryLog = logging.getLogger('telemetry_logging')
        debugLog.handlers = []
        telemetryLog.handlers = []
    def stop(self):
        self.marsCommandQueue.put(MARS_EXIT_COMMAND)

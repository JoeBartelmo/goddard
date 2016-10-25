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

import logging
import threading
import sys
import time

logger = logging.getLogger('mars_logging')

class TelemetryThread(threading.Thread):
    def __init__(self, jetson):
        super(TelemetryThread, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while self.stopped() == False:
            self._jetson.telemetryController()
        logger.info('Telemetry thread Stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()

class WatchdogUpdate(threading.Thread):
    def __init__(self, arduino, interval = 9):
        super(WatchdogUpdate, self).__init__()
        self._jetson = jetson
        self._stop = threading.Event()
        self._interval = interval

    def run(self):
        while self.stopped == False:
            #send w to arduino
            logger.debug('Sending W to update arduino watchdog timer')
            time.sleep(interval)
        logger.info('Watchdog update thread Stopped')

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()


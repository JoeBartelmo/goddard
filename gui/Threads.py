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

import json
import threading
import time
from Queue import Empty
from openCvTimeoutHandler import *
import logging
logger = logging.getLogger('mars_logging')

class VideoThread(threading.Thread):
    '''
    Thread Responsible for maintaining connection for a given RTP stream.
    It makes reference calls to the openCvCapture module to start/stop
    the stream in a resonable timeframe, also keeps the GUI responsive
    during a refresh or initialization.
    '''
    def __init__(self, name, rtspLocation, queue):
        super(VideoThread, self).__init__()
        self._vidcap = None
        self._openCvCapture = OpenCvCapture(name, rtspLocation)
        self._openCvCapture.start()
        self._queue = queue
        self._stop = threading.Event()
        self._name = name

        self.transformFunction = None

    def run(self):
        #wait until timeout has been met before we attempt to connect
        #to a camera that may or may not exist
        logger.info('Attempting to start Vidcap on ' + self._name)
        while (self._openCvCapture.is_alive()):
            time.sleep(0.01)
        
        if self._openCvCapture.isConnected():
            self._vidcap = self._openCvCapture.getVideoCapture()
            logger.debug('Starting VideoThread @ ' + str(time.time()))
            while self.stopped() == False:
                flag, frame = self._vidcap.read()

                if not flag:
                    continue
                
                self._queue.put(frame)

            logger.debug('Killing Video Thread')
            self._vidcap.release()
            self._openCvCapture.disconnect()

    def empty_queue(self):
        while self._queue.empty() == False:
            try:
                __ = self._queue.get(False)
            except Empty:
                self._queue.task_done()
                break

    def get_ideal_images(self):
        self.ideal_pump = []

        for s in self.streams:
            if s._vidcap is not None and s._vidcap.isOpened():
                flag, frame = s._vidcap.read()
                if not flag:
                    continue
                ideal_keypoint = self.fast.detect(frame, None)
                self.ideal_pump.append(stealth_pumpkin(frame, ideal_keypoint))

    def stop(self):
        self._stop.set()
   
    def transform(self, func):
        self.transformFunction = func

    def stopped(self):
        return self._stop.isSet()


class TelemetryThread(threading.Thread):
    '''
    Thread responsible for updating the telemetry widget.

    Additionally, and this is kind of unfortunate. We need
    to be able to update a seperate queue for the BeamGapWidget.

    This cannot be done on the client side because we use the
    listener class to grab the data, in that class it is unknown 
    as to whether or not the listener is receiving the telmetry data.

    So in this class I extract Valmar from the telemetry data and
    pipe it into a seperate queue.
    '''
    def __init__(self, telem_widget, client_queue, beam_gap_queue):
        super(TelemetryThread, self).__init__()
        self._queue = client_queue
        self._beam_gap_queue = beam_gap_queue
        self._widget = telem_widget
        self._stop = threading.Event()

    def run(self):
        while self.stopped() == False:
            try:
                record = self._queue.get(False)
                telemetryData = json.loads(record.msg)
                self._widget.set_telemetry_data(telemetryData)

                #extract valmar data and pipe it into beamgapqueue
                if telemetryData["Valmar"] is not None:
                    self._beam_gap_queue.put(telemetryData["Valmar"])
                    #literally only a warning so it stands out in log
                    logger.warning('Received Beam Gap Data!')
            except Empty:
                pass

    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()



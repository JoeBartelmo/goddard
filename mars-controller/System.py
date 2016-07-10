import logging
import time
import sys
from Arduino import Arduino
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Threads import InputThread, StatisticsThread

class System(object):

    def __init__(self, config, timestamp):

        #Init devices
        self._arduino, self._mars = self.initDevices(config)

        #Prepare stream
        self._stream = Stream(config, timestamp)

        logging.info("Connecting Jetson")
        self._jetson = Jetson(self._arduino, config, self._mars, timestamp, self._stream)
        time.sleep(.5)
        logging.info("All devices connected")
        logging.info("System initialized.")
        answer = raw_input("Would you like to start? Y/N: ")
        if answer.lower() in ('y', 'yes'):
            print ("The threads will start. ")
            self._jetson.start()






    def initDevices(self, config):

        #self._arduino.arduinoPowerOn()
        logging.info("Connecting arduino...")
        logging.info('Attempting to connect Arduino')
        myArduino = Arduino(config)
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logging.info("Starting Mars...")
        myMars = Mars(myArduino, config)
        time.sleep(.5)


        return myArduino, myMars









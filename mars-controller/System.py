import logging
import time
import sys
from Arduino import Arduino
from ArduinoDevices import Motor, LED
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Threads import InputThread, StatisticsThread

class System(object):

    def __init__(self, config, timestamp):

        #Init devices

        self._devices = self.initDevices(config)

        #Prepare stream
        self._devices['Stream'] = Stream(config, timestamp)

        logging.info("Connecting Jetson")
        self._jetson = Jetson(self._devices, config, timestamp)
        time.sleep(.5)


        logging.info("All devices connected")
        logging.info("System initialized.")


        answer = raw_input("Would you like to start? Y/N: ")
        if answer.lower() in ('y', 'yes'):
            print ("The system will start. ")
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

        devices = {
                    'Motor': Motor(),
                    'LED': LED(),
                    'Mars': myMars,
                    'Arduino': myArduino,

        }
        return devices









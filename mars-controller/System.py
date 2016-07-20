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
        myArduino = Arduino(config) #this line must be changed if multiple arduinos are used
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logging.info("Starting Mars...")
        myLED = LED()
        myMotor = Motor()
        myMars = Mars(myArduino, config, self._jetson._valmar, self._jetson._watchdog,myLED,myMotor)
        time.sleep(.5)

        devices = {
                    'Motor': myMotor,
                    'LED': myLED,
                    'Mars': myMars,
                    'Arduino': myArduino,

        }
        return devices









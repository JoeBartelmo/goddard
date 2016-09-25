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
import time
import sys
from Arduino import Arduino
from ArduinoDevices import Motor, LED
from Jetson import Jetson
from Mars import Mars
from Stream import Stream
from Threads import TelemetryThread
from Watchdog import Watchdog
from Valmar import Valmar
from GpioPin import GpioPin

logger = logging.getLogger('mars_logging')

class System(object):

    def __init__(self, config, timestamp, q = None, watchdogQueue = None, marsOnlineQueue = None):

        #assign queues
        self._watchdogQueue = watchdogQueue
        self._marsOnlineQueue = marsOnlineQueue

        #Init devices
        self._devices = self.initDevices(config)

        #Prepare stream
        self._devices['Stream'] = Stream(config, timestamp)

        logger.info("Connecting Jetson")
        self._jetson = Jetson(self._devices, config, timestamp, q)
        time.sleep(.5)


        logger.info("All devices connected")
        logger.info("System initialized.")
        
        if q is None:
            answer = raw_input("Would you like to start? Y/n: ")
            if answer.lower() == 'n' or answer.lower() == 'no':
                self._jetson.exit()
            else:
                self._jetson.start()
        else:
            self._jetson.start()

    def initDevices(self, config):
        """
        Prepare the arduino, the LED, the motor, and the composite mars object with corresponding VALMAR and devicehash
        for jetson.
        :param config:
        :return:
        """

        #self._arduino.arduinoPowerOn()
        logger.info("Connecting arduino...")
        myArduino = Arduino(config)
        time.sleep(.5)

        #Flush buffers
        myArduino.flushBuffers()

        logger.info("Starting Mars...")
        myPinHash = {'resetArduino': GpioPin(57),
                         'connectionLED': GpioPin(163),
                         'warningLED': GpioPin(164),
                         'batteryLED': GpioPin(165),
                         'motorRelay': GpioPin(166),
                         'ledRelay': GpioPin(160),
                         'laserRelay': GpioPin(161),
                         'relay4': GpioPin(162)
                         }
        myLED = LED()
        myMotor = Motor()
        myMars = Mars(myArduino, config, myLED, myMotor, myPinHash, self._watchdogQueue, self._marsOnlineQueue)
        time.sleep(.5)
        myValmar = Valmar(config, myMars)


        devices = {
                    'Motor': myMotor,
                    'LED': myLED,
                    'Mars': myMars,
                    'Arduino': myArduino,
                    'Valmar': myValmar,
                    'pinHash': myPinHash
        }
        return devices
myValmar,
                    'pinHash': myPinHash
        }
        return devices

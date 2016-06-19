'''
ark9719
6/17/2016
'''
import serial
import time
import logging
import sys

class Arduino(object):

    def __init__(self, config):
        self._config = config
        self._init = False #False until initialized
        self._timeInit = time.time()

        try:
            print("Attempting to connect Arduino")
            self._controller = serial.Serial(self._config.communications.arduinoPath, self._config.constants.baudRate)
            self._init = True
            logging.info('Arduino connected')
            print("Arduino connected.")

        except serial.serialutil.SerialException:
            logging.info("Arduino didn't connect.")
            print("arduino not connected or device path wrong")
            print("check MARS user manual for details")
            print("unable to continue, program will now terminate")
            sys.exit()


    def flushBuffers(self):
        """
        Function to flush arduinos serial buffers
        :return:
        """
        if(self._init):
            self._controller.flushInput()
            self._controller.flushOutput()
        else:
            print("Arduino has not been initialized!")

    def flushInput(self):
        if(self._init):
            self._controller.flushInput()
        else:
            print("Arduino has not been initialized!")

    def flushOutput(self):
        if(self._init):
            self._controller.flushOutput()
        else:
            print("Arduino has not been initialized!")

    def write(self, controlCode):
        """
        Writes the control code to the arduino over the serial buffers
        :param controlCode:
        :return:
        """
        if (self._init):
            self._controller.write(controlCode) #send control code over
        else:
            print("Arduino has not been initialized!")


    def inWaiting(self):
        """
        Return waiting time
        :return:
        """
        return self._controller.inWaiting()



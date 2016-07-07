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
        logging.info("System initialized.")

        logging.info("Starting threads...")
        self.startThreads()




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




    def startThreads(self):
            """
            This method starts the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """
            logging.info("Attempting to start threads")

            try:
                inputT = InputThread(self._jetson)
                statsT = StatisticsThread(self._jetson)
                inputT.start()
                statsT.start()
            except Exception as e:
                logging.WARNING("error starting threads ({})".format(e))
                logging.WARNING("program will terminate")
                sys.exit()




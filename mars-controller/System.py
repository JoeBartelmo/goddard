import logging
import time
import sys
from Arduino import Arduino
from Jetson import Jetson
from Mars import Mars
from Threads import InputThread, StatisticsThread

class System(object):

    def __init__(self, config, timestamp):

        #Init devices
        self._jetson, self._arduino, self._mars = self.initDevices(config, timestamp)

        logging.info("System initialized.")

        logging.info("Starting threads...")
        self.startThreads()





    def initDevices(self, config, timestamp):

        #self._arduino.arduinoPowerOn()

        logging.info("Connecting arduino...")
        logging.info('Attempting to connect Arduino')
        myArduino = Arduino(config)
        time.sleep(1)

        #Flush buffers
        myArduino.flushBuffers()

        logging.info("Starting Mars...")
        myMars = Mars(myArduino, config)
        time.sleep(1)

        logging.info("Connecting to Jetson")
        myJetson = Jetson(myArduino, config, myMars, timestamp)
        time.sleep(1)


        return myJetson, myArduino, myMars




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




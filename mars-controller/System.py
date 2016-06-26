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

        #start threads
        time.sleep(1) #Give the arduino time to start
        self.startThreads()

        logging.info("System initialized.")



    def initDevices(self, config, timestamp):

        print("Connecting arduino...")
        logging.info('Attempting to connect Arduino')
        myArduino = Arduino(config)

        #Flush buffers
        myArduino.flushBuffers()

        print("Starting Mars...")
        myMars = Mars(myArduino, config)

        print("Starting output...")
        myJetson = Jetson(myArduino, config, myMars, timestamp)


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




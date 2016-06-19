'''
ark9719
6/17/2016
'''

import threading
from CodeInput import ConcreteLEDInput
from CodeInput import ConcreteMotorInput
from CodeInput import ConcreteStreamInput
import logging
import pyping
import csv
import time
import sys

class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, arduino, config, mars):
        self._arduino = arduino
        self._mars = mars
        self._lastMotion = 'None yet'
        self._lastLED = 'None yet'
        self._lastStream = 'None yet'
        self._config = config
        self._lastRead = 0.0
        self._connected = self.connectionPing()


    def startThreads(self):
        """
        This method starts the two threads that will run for the duration of the program. One scanning for input,
        the other generating, displaying, and saving data.
        :return:
        """
        logging.info("Attempting to start threads")
        dataThread = threading.Thread(target = self.statisticsController())
        inputThread =  threading.Thread(target = self.repeatInput())
        # pingingThread = threading.Thread(target = m.connection_check)
        #
        try:
            dataThread.start() #read_print_save() thread
            inputThread.start() #repeat_input() thread
            #pingingThread.start() #connection_check() thread
        except Exception as e:
            logging.info("error starting Multithreading ({})".format(e))
            logging.info("program will terminate")
            sys.exit()

    def repeatInput(self):
        """
        Continuesly scans for controller input first identifying the type of command then checking validity
        before writing to the arduino and storing the last command.

        :return:
        """
        while True:
            #Prompt for input
            controlCode = raw_input("LED or Motion Control code: ")

            #Create a Motor or LED code object
            if controlCode[0] == 'M':
                myCodeInput = ConcreteMotorInput(controlCode)
            elif controlCode[0] == 'L':
                myCodeInput = ConcreteLEDInput(controlCode)
            elif controlCode[0] == 'S':
                myCodeInput = ConcreteStreamInput(controlCode)
            else:
                logging.info("Invalid leading character. L, M, or S")
                break

            #Check for validity
            if myCodeInput.valid():

                #Write to Arduino
                print(controlCode + " inputed succesfully (valid).")
                self._arduino.write(controlCode)
                logging.info("Control code written to Arduino.")

                #Store the last code
                if(myCodeInput._type == 'M'):
                    self._lastMotion = controlCode
                if(myCodeInput._type == 'L'):
                    self._lastLED = controlCode
                if(myCodeInput._type == 'S'):
                    self._lastStream = controlCode

            else:
                logging.info("Code is invalid.")


    def statisticsController(self):
        """
        The loop for gathering, displaying, and saving data.
        :return:
        """

        while True:

            logging.info("Generating Statistics...")
            self._mars.generateStatistics()#Perform a statistics read

            logging.info("Displaying Statistics...")
            print (self.displayStatistics(self._mars._statistics)) #Display human readable statistics

            logging.info("Saving statistics...")
            #self.saveStats(self._mars._statistics) added this to last line of displayStats for testing

            self._mars._integTime = time.time()

    def displayStatistics(self, data):
        """
        Takes the data created by Mars and prints it, human readable.
        :param data:
        :return:
        """

        runClock = time.time() - self._arduino._timeInit
        minutes,seconds = divmod(runClock, 60)

        minSecString = 'Time running: ' + str(int(minutes)) + ":" + str(int(seconds)) + " {  "
        distanceString = str(data['totalDisplacement'])+"meters, "
        speedString = str(data['speed']) + "m/s, "
        powerString = str(data['power']) + "Watts, "
        batteryString = str(data['batteryRemaining']) + "%, "
        #integration time isn't needed for operator
        if self._connected == True:
            connectionString = "Connected,  "
        else:
            connectionString = "Disconnected, "

        #raw data off of Arduino
        rpmString = str(data['rpm']) + "rpm, "
        voltageString = str(data['sysV']) + "V, "
        currentString = str(data['sysI']) + "A, "

        #last commands set by operator
        mCodeString = 'motion command: ' + self._lastMotion + ', '
        lCodeString = 'LED command: ' + self._lastLED + ', '
        sCodeString = 'stream command: ' + self._lastStream + ' } '


        operatorString = minSecString + distanceString + speedString + \
        powerString + batteryString + rpmString + voltageString + \
        currentString +connectionString + mCodeString + lCodeString + \
		sCodeString + '\r\n'

        logging.info("Saving stats.")
        self.saveStats(operatorString)

        return operatorString


    def saveStats(self, data):
        """
        This is the method in control of saving data generated by Mars onto the harddisk.
        :param data:
        :return:
        """
        try:
            fileName =  'logs/'+  self._config.log.name + '_machine_log.csv'
            with open(fileName, 'a') as rawFile:
                rawWriter = csv.writer(rawFile)
                rawWriter.writerow(data)

        except Exception as e:
            logging.info("unable to log data because: \r\n {}".format(e))

    def connectionMonitor(self):
        """
        This method is intended to monitor the connection with the controller.
        :return:
        """
        while True:
            time.sleep(5)
            if (not self.connectionPing()):
                self._connected = False
                logging.info("Connection broken")


    def connectionPing(self):
        """
        This method performs a simple ping to the controller.
        :return:
        """
        request = pyping.ping(self._config.communications.masterIP)
        return (request.ret_code == 0)

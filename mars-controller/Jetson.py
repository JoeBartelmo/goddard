'''
ark9719
6/17/2016
'''

from CodeInput import ConcreteLEDInput, ConcreteStreamInput, ConcreteMotorInput, ConcreteSystemInput
from Watchdog import Watchdog
import logging
import csv
import time
import json
import subprocess


class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, arduino, config, mars, timestamp, stream):
        self._arduino = arduino
        self._stream = stream
        self._mars = mars
        self._timestamp = timestamp
        self._config = config
        self._header = False
        self.initCommands()
        self._watchdog = Watchdog(self)



    def repeatInput(self):
        """
        Continuesly scans for controller input first identifying the type of command then checking validity
        before writing to the arduino and storing the last command.
        :return:
        """

        while True:
            #Prompt for input
            controlCode = raw_input("LED, motion, stream, or control code: \n")
            myCodeInput = self.recieveInput(controlCode)
            if myCodeInput == None: continue
            if myCodeInput.valid():
                myCodeInput.issue()
            else:
                logging.info("Invalid code.")
                continue


    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        print("Control code: " + controlCode)

        if controlCode[0] == 'M':
            return ConcreteMotorInput(controlCode, self._arduino)
        elif controlCode[0] == 'L':
            return ConcreteLEDInput(controlCode, self._arduino)
        elif controlCode[0] == 'S':
            return ConcreteStreamInput(controlCode, self._stream)
        elif controlCode in (self._sysCommands):
            return ConcreteSystemInput(controlCode, self, self._arduino, self._mars, self._sysCommands)
        elif controlCode in ('forward', 'backward'):
            return ConcreteSystemInput(controlCode, self, self._arduino, self._mars, self._sysCommands)
        else:
            return logging.info("Invalid control code. Check documentation for command syntax.")


    def statisticsController(self):
        """
        The loop for gathering, displaying, and saving data.
        :return:
        """

        while True:

            logging.info("Generating Statistics...")
            self._mars.generateStatistics()

            logging.info("Displaying Statistics...")
            print(self.displayStatistics(self._mars._statistics))

            logging.info("Saving statistics...")
            self.saveStats(self._mars._statistics)

            #Set the integ time to the time of the last read for calculations
            self._mars._integTime = time.time()
            print("-------------------------------")

            #self._watchdog.sniffPower()
            #self._watchdog.sniffUltrasonicDistance()
            #self._watchdog.react()

    def displayStatistics(self, data):
        """
        Takes the data created by Mars and prints it, human readable.
        :param data:
        :return:
        """
        return json.dumps(data) 


    def saveStats(self, data):
        """
        This is the method in control of saving data generated by Mars onto the harddisk.
        :param data:
        :return:
        """
        #If the header to the file isn't written, write it.
        if (not self._header ):
            fileName = self._config.logging.outputPath + '/output/' + self._timestamp + '/' + self._config.logging.logName + '_machine_log.csv'
            with open(fileName, 'a') as rawFile:
                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writeheader()
            self._header = True

        try:
            fileName = self._config.logging.outputPath + '/output/' + self._timestamp + '/' + self._config.logging.logName + '_machine_log.csv'
            with open(fileName, 'a') as rawFile:
                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writerow(data)

        except Exception as e:
            logging.info("unable to log data because: \r\n {}".format(e))


    def systemRestart(self):
        logging.info("initiating safe restart")
        logging.info("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logging.info("restarting this computer")
        logging.info("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo reboot'], shell=True)


    def systemShutdown(self):
        logging.info("initiating safe shutdown")
        logging.info("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logging.info("shutting downn this computer")
        logging.info("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo poweroff'], shell=True)

    def initCommands(self):
        self._sysCommands = {'sys-shutdown': self.systemShutdown,
                                'sys-restart': self.systemRestart,
                                'a-poweron': self._arduino.powerOn,
                                'a-poweroff': self._arduino.powerOff,
                                'a-restart': self._arduino.reset,
                                'recall': self._mars.recall,
                                # 'break': system.break_all_circuits(), \
                                'stream open': self._stream.open,
                                'stream close': self._stream.close,
                                'brake': self._arduino.brake,
                                #'exit': self.exit
                             }



    def exit(self):
        self._sysCommands['brake']()
        #self._sysCommands['a-poweroff']()
        self._sysCommands['stream close']()







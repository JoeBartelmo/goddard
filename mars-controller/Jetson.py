'''
ark9719
6/17/2016
'''

from CodeInput import ConcreteLEDInput, ConcreteStreamInput, ConcreteMotorInput, ConcreteSystemInput
from GpioPin import GpioPin
from Watchdog import Watchdog
from Threads import InputThread, StatisticsThread
import logging
import csv
import sys
import time
import json
import subprocess


class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, devices, config, timestamp):

        self._devices = devices
        self.initDevices()

        self._pinHash = self.initPins()
        self.initCommands()

        self._timestamp = timestamp
        self._config = config
        self._header = False

        self._watchdog = Watchdog(self)

    def initDevices(self):
        self._arduino = self._devices['Arduino']
        self._stream = self._devices['Stream']
        self._mars = self._devices['Mars']
        self._motor = self._devices['Motor']
        self._motor._arduino = self._arduino
        self._led = self._devices['LED']
        self._led._arduino = self._arduino

    def initPins(self):
        """
        Create 8 pin objects
        """

        pinHash = {'resetArduino': GpioPin(166),
                    'connectionLED': GpioPin(163),
                    'warningLED': GpioPin(164),
                    'batteryLED': GpioPin(165),
                    'motorRelay': GpioPin(57),
                    'ledRelay': GpioPin(160),
                    'laserRelay': GpioPin(161),
                    'relay4': GpioPin(162)
                 }

        return pinHash

    def initCommands(self):
        self._sysCommands = {'sys-shutdown': self.systemShutdown,
                                'sys-restart': self.systemRestart,
                                'a-poweron': self._arduino.powerOn,
                                'a-poweroff': self._arduino.powerOff,
                                'a-restart': self._arduino.reset,
                                'recall': self._mars.recall,
                                'stream open': self._stream.open,
                                'stream close': self._stream.close,
                                'brake': self._arduino.brake,
                                'motors off': self._pinHash['motorRelay'].toggleOn ,
                                'lasers off': self._pinHash['laserRelay'].toggleOn,
                                'led off': self._pinHash['ledRelay'].toggleOn,
                                'hibernate': self.hibernate,
                                'start': self.start,
                                'exit': self.exit
                             }


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



    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        print("Control code: " + controlCode)

        if controlCode in self._motor._motorCodes:
            return self._motor.issue(controlCode, self._arduino)
        elif controlCode in self._led.LEDcodes:
            return self._led.issue(self._arduino)
        elif controlCode in self._stream._streamCodes:
            return self._stream.issue(controlCode)
        elif controlCode in self._sysCommands:
            self._sysCommands[controlCode]()
            #return ConcreteSystemInput(controlCode, self, self._arduino, self._mars, self._sysCommands)
        else:
            return logging.info("Invalid control code. Check documentation for command syntax.")



    def statisticsController(self):
        """
        The loop for gathering, displaying, and saving data.
        :return:
        """

        while True:

            logging.debug("Generating Statistics...")
            self._mars.generateStatistics()

            logging.debug("Displaying Statistics...")
            logging.info(self.displayStatistics(self._mars._statistics))

            logging.debug("Saving statistics...")
            self.saveStats(self._mars._statistics)

            #Set the integ time to the time of the last read for calculations
            self._mars._integTime = time.time()

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

    def manageThreads(self, toggle):
            """
            This method starts the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """

            if (toggle == 'start'):
                logging.info("Attempting to start threads")

                try:
                    self._inputT = InputThread(self)
                    self._statsT = StatisticsThread(self)
                    self._inputT.start()
                    self._statsT.start()
                except Exception as e:
                    logging.WARNING("error starting threads ({})".format(e))
                    logging.WARNING("program will terminate")
                    sys.exit()
            elif (toggle == 'stop'):
                logging.info("Attempting to stop threads")

                try:
                    self._inputT.stop()
                    self._statsT.stop()
                except Exception as e:
                    logging.WARNING("error starting threads ({})".format(e))
                    logging.WARNING("program will terminate")
                    sys.exit()


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

    def start(self):
        self._pinHash['motorRelay'].changeState(0)
        logging.info("Motor relay started")
        self._pinHash['ledRelay'].changeState(0)
        logging.info("LED relay started")
        self._pinHash['laserRelay'].changeState(0)
        logging.info("Laser relay started")

        logging.info("Starting motor...")
        self._motor.start()

        logging.info("Starting stream...")
        self._sysCommands['stream open']()

        logging.info("Starting threads...")
        self.manageThreads('start')

    def exit(self):

        logging.info("Stopping threads")
        self.manageThreads('stop')

        logging.info("Braking motor...")
        self._motor.brake()

        logging.info("Closing stream...")
        self._sysCommands['stream close']()

        logging.info(("Turning off LEDs..."))
        self._led.issue(0)

        self._pinHash['motorRelay'].changeState(1)
        logging.info("Motor relay stopped")
        self._pinHash['ledRelay'].changeState(1)
        logging.info("LED relay stopped")
        self._pinHash['laserRelay'].changeState(1)
        logging.info("Laser relay stopped")

        sys.exit()


    def hibernate(self):
        self._pinHash['motorRelay'].changeState(1)
        logging.info("Motor relay ended")
        self._pinHash['ledRelay'].changeState(1)
        logging.info("LED relay ended")
        self._pinHash['laserRelay'].changeState(1)
        logging.info("Laser relay ended")
        self._stream.close()

    def turnOnComponent(self,indentifier):
        self._pinHash[indentifier].changeState(0) #inverted Logic: 0 --> On

    def turnOffComponent(self,indentifier):
        self._pinHash[indentifier].changeState(1) #inverted Logic: 1 --> Off

    def resetArduino(self):

        self.turnOffComponent("resetArduino")
        time.sleep(.2)
        self.turnOnComponent("resetArduino")












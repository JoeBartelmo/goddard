'''
ark9719
6/17/2016
'''

from GpioPin import GpioPin
from Watchdog import Watchdog
from Threads import InputThread, TelemetryThread
from Valmar import Valmar
from GraphUtility import GraphUtility
import logging
import csv
import sys
import time
import json
import subprocess
import base64

class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, devices, config, timestamp, q = None):
        self._devices = devices

        self._pinHash = self._devices['pinHash']
        self._devices['Watchdog'] = Watchdog(config, self._devices['Arduino'], self._devices['Mars'], self._pinHash)
        self.initDevices()
        self._inputT = InputThread(self)
        self._statsT = TelemetryThread(self)
        self.initCommands()

        self._timestamp = timestamp
        self._config = config
        self._header = False
        self._q = q
        self.graphUtil = GraphUtility(config)

        self._pauseTelemetry = False

    def initDevices(self):
        """
        Make every device in the device hash accessible via Jetson
        :return:
        """
        self._arduino = self._devices['Arduino']
        self._stream = self._devices['Stream']
        self._mars = self._devices['Mars']
        self._motor = self._devices['Motor']
        self._motor._arduino = self._arduino
        self._led = self._devices['LED']
        self._led._arduino = self._arduino
        self._watchdog = self._devices['Watchdog']
        self._valmar = self._devices['Valmar']



    def initCommands(self):
        """
        Initialize a list of valid system commands
        :return:
        """
        self._sysCommands = {'system shutdown': self.systemShutdown,
                                'system restart': self.systemRestart,
                                'recall': self._watchdog.recall,
                                'stream open': self._stream.open,
                                'stream close': self._stream.close,
                                'reset arduino': self.resetArduino,
                                'motor off': self._pinHash['motorRelay'].toggleOff,
                                'motor on' : self._pinHash['motorRelay'].toggleOn,
                                'laser off': self._pinHash['laserRelay'].toggleOff,
                                'laser on' : self._pinHash['laserRelay'].toggleOn,
                                'led off': self._pinHash['ledRelay'].toggleOff,
                                'led on' : self._pinHash['ledRelay'].toggleOn,
                                'hibernate': self.hibernate,
                                'start': self.start,
                                'exit': self.exit,
                                'list logs': self.listLogs,
                                'watchdog off': self._watchdog.disable,
                                'watchdog on': self._watchdog.enable,
                                'valmar off': self._valmar.disable,
                                'valmar on': self._valmar.enable
                             }


    def safeInput(self):
        """
        Continuesly scans for controller input first identifying the type of command then checking validity
        before writing to the arduino and storing the last command.
        :return:
        """

        #Prompt for input
        if self._q is None:
            controlCode = raw_input("LED, motion, stream, or control code: \n")
        else:
            controlCode = self._q.get()
        myCodeInput = self.recieveInput(controlCode)



    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        logging.info("Control code: " + controlCode)

        if controlCode in self._motor._motorCodes:
            return self._motor.issue(controlCode, self._arduino)
        elif "forward" in controlCode or "backward" in controlCode or "brake" in controlCode:
            return self._motor.movement(controlCode)
        elif "brightness" in controlCode:
            return self._led.issue(self._arduino, controlCode)
        elif controlCode in self._stream._streamCodes:
            return self._stream.issue(controlCode)
        elif controlCode in self._sysCommands:
            self._sysCommands[controlCode]()
        elif 'graph' in controlCode:
            self.graph(controlCode)
        else:
            return logging.info("Invalid control code. Check documentation for command syntax.")



    def telemetryController(self):
        """
        The controller for generating(Reading) data, checking it for errors and saving it.
        :return:
        """
        if self._pauseTelemetry == False:
            logging.debug("Generating Telemetry...")
            telemetry = self._mars.generateTelemetry()

            #inject telemetry updates
            telemetry.update(self._watchdog.watch(telemetry))
            telemetry.update(self._valmar.updateTelemetry())
            logging.debug("Displaying Telemetry...")
            logging.info(self.displayTelemetry(self._mars._telemetry))
            logging.debug("Saving telemetry...")
            self.saveStats(self._mars._telemetry)

            #Set the integ time to the time of the last read for calculations
        else:
            self._arduino.flushBuffers()
            pass
        self._mars._integTime = time.time()

    def displayTelemetry(self, data):
        """
        Transforms the data into a more readable output for logging
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
        self._filename = self._config.logging.output_path + '/output/' + self._config.user_input.log_name + '-' + self._timestamp + '/' + self._config.user_input.log_name + '_machine_log.csv'
        #If the header to the file isn't written, write it.
        try:
            with open(self._filename, 'a') as rawFile:
                #If the header to the file isn't written, write it.
                if (not self._header):
                    rawWriter = csv.DictWriter(rawFile, data.keys())
                    rawWriter.writeheader()
                    self._header = True

                rawWriter = csv.DictWriter(rawFile, data.keys())
                rawWriter.writerow(data)

        except Exception as e:
            logging.info("unable to log data because: \r\n {}".format(e))

    def manageThreads(self, toggle):
            """
            This method manages the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """
            if (toggle == 'start'):
                logging.info("Attempting to start threads")

                try:

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
                    logging.WARNING("error stopping threads ({})".format(e))
                    logging.WARNING("program will terminate")
                    sys.exit()


    def systemRestart(self):
        """
        Restart the entire system, arduino included
        :return:
        """
        logging.info("initiating safe restart")
        logging.info("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logging.info("restarting this computer")
        logging.info("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo reboot'], shell=True)


    def systemShutdown(self):
        """
        Shutdown the system
        :return:
        """
        logging.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logging.info("shutting downn this computer")
        logging.info("this connection will be lost")
        subprocess.call(['sudo poweroff'], shell=True)

    def start(self):
        """
        Start command for the program. Start all the relays, the motor, stream, and threads
        :return:
        """
        self._pinHash['motorRelay'].toggleOn()
        logging.info("Motor circuit closed")
        self._pinHash['ledRelay'].toggleOn()
        logging.info("LED circuit closed")
        self._pinHash['laserRelay'].toggleOn()
        logging.info("Laser circuit closed")

        logging.info("Starting motor...")
        self._motor.start()

        logging.info("Starting stream...")
        self._stream.open()

        logging.info("Starting threads...")
        self.manageThreads('start')





    def manual(self):
        """
        Manual mode for the jetsons means only starting the input thread allowing the user to start
        telemetry generation later
        :return:
        """
        self._inputT.start()

    def exit(self):
        """
        Exit command for stopping the program.
        :return:
        """
        logging.info("Stopping threads")
        self.manageThreads('stop')

        logging.info("Braking motor...")
        self._motor.brake()
        time.sleep(2) #necessary to make sure Mars moves to a stop

        logging.info("Closing stream...")
        self._sysCommands['stream close']()

        logging.info(("Turning off LEDs..."))
        self._led.issue(self._arduino, "brightness 0")

        self._pinHash['motorRelay'].toggleOff()
        logging.info("Motor relay stopped")
        self._pinHash['ledRelay'].toggleOff()
        logging.info("LED relay stopped")
        self._pinHash['laserRelay'].toggleOff()
        logging.info("Laser relay stopped")

        self.manageThreads('stop')

        sys.exit()


    def hibernate(self):
        """
        TODO: Hibernate function for Jetson
        :return:
        """
        self._pinHash['motorRelay'].toggleOff()
        logging.warning("motor circuit opened")
        self._pinHash['ledRelay'].toggleOff()
        logging.warning("led circuit opened")
        self._pinHash['laserRelay'].toggleOff()
        logging.warning("laser circuit opened")
        self._stream.close()
        logging.warning("closing video stream")
        self._valmar.issueCommand("enable",False)
        logging.warning("pausing VALMAR gap measurement system")

        self._pauseTelemetry = True
        logging.warning("pausing telemetry")

        logging.info("system hibernating")


    def resume(self):
        """
        this method is meant to resume normal function after hibernation
        :return:
        """
        self._pinHash['motorRelay'].toggleOn()
        logging.info("Motor circuit closed")
        self._pinHash['ledRelay'].toggleOn()
        logging.info("LED circuit closed")
        self._pinHash['laserRelay'].toggleOn()
        logging.info("Laser circuit closed")

        logging.info("All circuits closed and ready for use")

        logging.info("Resuming stream...")
        self._stream.open()


    def resetArduino(self):
        """
        Reset arduino system command
        :return:
        """
        self._pinHash["resetArduino"].toggleOn()
        time.sleep(.2)
        self._pinHash["resetArduino"].toggleOff()

    def graph(self, graphCommand):
        #This is kinda hacky, but we want to keep mars independant of the server
        #usually we would want to initiate a tcp-ip stream and send our pdf over
        #packets. To do this we would need to have mars have some 'knowledge' of 
        #the server. As I said, that's not preferred.

        #My solution is to base64 encode the file, and send it via the logging
        #this simplifies the entire process, and keeps us from coupling
        graphCommand = graphCommand.split(' ')
        if len(graphCommand) > 1:
            self.graphUtil.generate_pdf(graphCommand[1])
        else:
            self.graphUtil.generate_pdf()
        self.logFile('telemetry_graphs.pdf')

    #Sends with structure: magic namelength delimiter name filedata
    #magicheader: <<<_file_record_>>>
    #namelength: integer
    #delimiter: _
    #filedata: the local file read in as base64
    def logFile(self, fileIn):    
        with open(fileIn, 'rb') as f:
            nameLength = str(len(fileIn))
            logging.info('<<<_file_record_>>>' + nameLength + '_' + fileIn + base64.b64encode(f.read()))

    def listLogs(self):
        logging.info(self.graphUtil.get_all_outputs())
 

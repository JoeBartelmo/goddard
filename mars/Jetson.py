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

from GpioPin import GpioPin
from Watchdog import Watchdog
from Threads import *
from Valmar import Valmar
from GraphUtility import GraphUtility
import logging
import csv
import sys
import time
import json
import subprocess
import base64

logger = logging.getLogger('mars_logging')
telemetryLogger = logging.getLogger('telemetry_logging')

class Jetson(object):
    """
    Jetson controls input from the controller, and manages the data sent back from the
    arduino/mars
    """

    def __init__(self, devices, config, timestamp, q = None, marsOnlineQueue = None):
        self._devices = devices

        self._pinHash = self._devices['pinHash']
        self._devices['Watchdog'] = Watchdog(config, self._devices['Arduino'], self._devices['Mars'], self._pinHash)
        self.initDevices()
        self._statsT = TelemetryThread(self)
        if config.arduino.using_watchdog_timer == True:
            self._watchdogT = WatchdogUpdate(self._arduino, config.arduino.update_time_s)
        self.initCommands()

        self._exit = False
        self._timestamp = timestamp
        self._config = config
        self._header = False
        self._q = q
        self.graphUtil = GraphUtility(config)

        self._marsOnlineQueue = marsOnlineQueue

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
                                'system hibernate': self.hibernate,
                                'system wake': self.wake,
                                'recall': self._watchdog.recall,
                                'stream on': self._stream.open,
                                'stream off': self._stream.close,
                                'motor off': self._pinHash['motorRelay'].toggleOff,
                                'motor on' : self._pinHash['motorRelay'].toggleOn,
                                #@depricated
                                #'laser off': self._pinHash['laserRelay'].toggleOff,
                                #'laser on' : self._pinHash['laserRelay'].toggleOn,
                                'led off': self._pinHash['ledRelay'].toggleOff,
                                'led on' : self._pinHash['ledRelay'].toggleOn,
                                'reset arduino': self._arduino.resetArduino,
                                #@depricated
                                #'start': self.start,
                                'exit': self.exit,
                                'list logs': self.listLogs,
                                'watchdog off': self._watchdog.disable,
                                'watchdog on': self._watchdog.enable,
                                'valmar off': self._valmar.disable,
                                'valmar on': self._valmar.enable,
                                'scan on': self.scan,
                                'scan off': self._watchdog.scanDisable,
                                'watchdogtimer on': self.startWatchdogThread,
                                'watchdogtimer off': self.stopWatchdogThread,
                                'help': self.listCommands
                             }

    def startWatchdogThread(self):
        if hasattr(self, '_watchdogT', None) is None:
            logger.info('Starting watchdog timer thread...')
            self._watchdogT = WatchdogUpdate(self._arduino, self._config.arduino.update_time_s)
            
    def stopWatchdogThread(self):
        if hasattr(self, '_watchdogT', None) is not None:
            logger.info('Stopping watchdog timer thread...')
            self._watchdogT.stop()
            self._watchdogT = None

    def listCommands(self):
        logger.info("\nsystem shutdown:\tShutdown M.A.R.S. Tk1\n" + \
                    "system restart:\t\tRestart M.A.R.S. Tk1\n" + \
                    "system hibernate:\t\tSuspends M.A.R.S. until reactivation\n" + \
                    "syste wake:\t\tTurns on all components that could be hibernated\n" + \
                    "motor [on|off]:\t\tIff on, then speed can be adjusted on motor\n" + \
                    "forward [0-9]:\t\tAssigns a forward speed to M.A.R.S.\n" + \
                    "backward [0-9]:\t\tAssigns a backward speed to M.A.R.S.\n" + \
                    "brake [on|off]:\t\tIff on, then motor cannot be enabled\n" + \
                    "led [on|off]:\t\tIff on, then brightness of leds can be set\n" + \
                    "brightness [0-9]:\tSets brightness of leds (useful for valmar)\n" + \
                    "reset arduino:\t\tWill attempt to restablish connection to the onboard arduino\n" + \
                    "exit:\t\t\tDisables all processes and stops M.A.R.S, server still online.\n" + \
                    "watchdog [on|off]:\tIf on, watchdog will recall or brake mars depending on scanmode when an issue is found.\n" + \
                    "watchdogtimer [on|off]:\tIf on, will send repeated pulse every 10 seconds to arduino.\n" + \
                    "scan [on|off]:\t\tWhen Toggled on, all of mars processes are automated\n" + \
                    "valmar [on|off]:\tOn by default, valmar gets beam gap data\n" + \
                    "list logs:\t\tDisplay all logs for all teams\n" + \
                    "graph [log_name]:\tGenerates a PDF graph of M.A.R.S. data for a given log (curent by default if none is supplied)")

    def scan(self):
        """
        Performs a set list of commands to automate mars
        """
        #enable watchdog
        self._watchdog.scanEnable()        
        #disengage brake
        self.recieveInput('brake off')
        #enable leds brightness @ 9 
        self.recieveInput('led on')
        self.recieveInput('brightness 9')
        #motor on forward half thrusters
        self.recieveInput('motor on')
        self.recieveInput('forward 5')

    def safeInput(self):
        """
        Continuesly scans for controller input first identifying the type of command then checking validity
        before writing to the arduino and storing the last command.
        :return:
        """

        #Prompt for input
        if self._q is None:
            try:
                controlCode = raw_input("Please Enter Command or \"help\"): \n")
            except KeyboardInterrupt:
                self.exit()
                return
        else:
            controlCode = self._q.get()
        myCodeInput = self.recieveInput(controlCode)
        
        return controlCode

    def recieveInput(self, controlCode):
        """
        Decipher the type of input. Motor, LED, Stream or System
        :param controlCode:
        :return: Return specialized command object
        """
        logger.info("Control code: " + controlCode)

        if controlCode in self._motor._motorCodes:
            return self._motor.issue(controlCode, self._arduino)
        elif "forward" in controlCode or "backward" in controlCode or "brake" in controlCode:
            return self._motor.movement(controlCode)
        elif "brightness" in controlCode:
            return self._led.issue(self._arduino, controlCode)
        elif controlCode in self._sysCommands:
            self._sysCommands[controlCode]()
        elif 'graph' in controlCode:
            self.graph(controlCode)
        #tripped if not valmar on|off
        elif 'valmar ' in controlCode and len(controlCode.split(' ')) == 3:
            valmarCommand = controlCode.split(' ')
            self._valmar.issueCommand(valmarCommand[1], valmarCommand[2])
        else:
            return logger.warning("Invalid control code. Check documentation for command syntax.")

    def inputLoop(self):
        """
        Runs a loop over the safeInput function, checks self._exit to determine
        whether or not it should hop out of the loop
        """
        while self._exit == False:
            self.safeInput()

    def telemetryController(self):
        """
        The controller for generating(Reading) data, checking it for errors and saving it.
        :return:
        """
        telemetry = None

        logger.debug("Generating Telemetry...")
        telemetry = self._mars.generateTelemetry()

        if telemetry is not None:
            #inject telemetry updates
            telemetry.update(self._watchdog.watch(telemetry))
            telemetry["Valmar"] = self._valmar.getBeamGapData()
            if telemetry["Valmar"] is not None:
                logger.debug('Valmar hit next beam')
            logger.debug("Displaying Telemetry...")
            #the logger sends the data over tcp
            telemetryLogger.info(self.displayTelemetry(self._mars._telemetry))
            logger.debug("Saving telemetry...")
            self.saveStats(self._mars._telemetry)

            #Set the integ time to the time of the last read for calculations
            self._mars._integTime = time.time()
        else:
            i = 0
            while self._arduino._init is False and i < 5:
                time.sleep(5)
                i += 1

    def displayTelemetry(self, data):
        """
        Transforms the data into a more readable output for logger
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
            logger.warning("unable to log data because: \r\n {}".format(e))

    def manageThreads(self, toggle):
            """
            This method manages the two threads that will run for the duration of the program. One scanning for input,
            the other generating, displaying, and saving data.
            :return:
            """
            if (toggle == 'start'):
                logger.info("Attempting to start threads")

                try:
                    self._statsT.start()
                    if getattr(self, '_watchdogT', None) is not None:
                        self._watchdogT.start()
                    self.inputLoop()
                except Exception as e:
                    logger.error("error starting threads ({})".format(e))
            elif (toggle == 'stop'):
                logger.info("Attempting to stop threads")

                try:
                    if getattr(self, '_watchdogT', None) is not None:
                        self._watchdogT.stop()
                    self._statsT.stop()
                except Exception as e:
                    logger.error("error stopping threads ({})".format(e))


    def systemRestart(self):
        """
        Restart the entire system, arduino included
        :return:
        """
        logger.warning("initiating safe restart")
        logger.warning ("shutting down arduino")
        self._arduino.powerOff()
        ### add functionality to cut power to motor controller
        logger.warning("restarting this computer")
        logger.warning("this connection will be lost")
        time.sleep(1)
        subprocess.call(['sudo reboot'], shell=True)


    def systemShutdown(self):
        """
        Shutdown the system
        :return:
        """
        logger.info("initiating safe shutdown")
        ### add functionality to cut power to motor controller
        logger.info("shutting downn this computer")
        logger.info("this connection will be lost")
        subprocess.call(['sudo poweroff'], shell=True)

    def start(self):
        """
        Start command for the program. Start all the relays, the motor, stream, and threads
        :return:
        """
        self._pinHash['motorRelay'].toggleOff()
        logger.info("Motor circuit closed")
        self._pinHash['ledRelay'].toggleOff()
        logger.info("LED circuit closed")
        self._pinHash['laserRelay'].toggleOff()
        logger.info("Laser circuit closed")

        logger.info("Starting motor...")
        self._motor.start()

        logger.info("Starting stream...")
        self._stream.open()

        logger.info("Starting threads...")
        self.manageThreads('start')

    def exit(self):
        """
        Exit command for stopping the program.
        :return:
        """
        logger.info("Stopping threads")
        self.manageThreads('stop')

        logger.info("Braking motor...")
        self._motor.brake()
        time.sleep(2) #necessary to make sure Mars moves to a stop

        logger.info("Closing stream...")
        self._sysCommands['stream off']()

        logger.info("Closing valmar...");
        self._valmar.disable()

        logger.info(("Turning off LEDs..."))
        self._led.issue(self._arduino, "brightness 0")

        self._pinHash['motorRelay'].toggleOff()
        logger.info("Motor Circuit turned off")
        self._pinHash['ledRelay'].toggleOff()
        logger.info("LED Circuit turned off")
        self._pinHash['laserRelay'].toggleOff()
        logger.info("Laser Circuit turned off")

        self._arduino.resetArduino()
        self._exit = True
        if self._marsOnlineQueue is not None:
            self._marsOnlineQueue.put(0)

    def hibernate(self):
        """
        Hibernate function for Jetson
        :return:
        """
        self._pinHash['motorRelay'].toggleOff()
        logger.warning("Toggle motorRelay off")
        self._pinHash['ledRelay'].toggleOff()
        logger.warning("Toggle ledRelay off")
        #depricated
        self._pinHash['laserRelay'].toggleOff()
        logger.warning("Toggle laser relay off")
        self._stream.close()
        logger.warning("Closing video stream")
        self._valmar.disable()
        logger.warning("Pausing VALMAR gap measurement system")

        logger.warning("Send the command \"wake\" to enable all disabled components")

    def wake(self):
        """
        Inverse hibration function for Jetson
        :return:
        """
        self._pinHash['motorRelay'].toggleOn()
        self._pinHash['ledRelay'].toggleOn()
        #depricated
        self._pinHash['laserRelay'].toggleOn()
        self._stream.open()
        self._valmar.enable()
        logger.info("Toggled On all relays, started maven and valmar!")

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


    def graph(self, graphCommand):
        graphCommand = graphCommand.split(' ')
        if len(graphCommand) > 1:
            self.graphUtil.generate_pdf(graphCommand[1])
        else:
            self.graphUtil.generate_pdf()

    def listLogs(self):
        logger.info(self.graphUtil.get_all_outputs())


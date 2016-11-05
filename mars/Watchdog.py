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
import subprocess

logger = logging.getLogger('mars_logging')

class Watchdog(object):
    def __init__(self, config, arduino, mars, pinHash):
        self._config = config
        self._arduino = arduino
        self._mars = mars

        self._levels = self._config.watchdog
        self._enableWatchdog = self._levels.enable_watchdog
        self._displayLogTimeout = self._levels.display_log_timeout
        self._lastDisplayTime = {"underVoltage":time.time() - self._config.watchdog.display_log_timeout,
                                    "overVoltage":time.time() - self._config.watchdog.display_log_timeout,
                                    "overCurrent":time.time() - self._config.watchdog.display_log_timeout,
                                    "batteryPercentage":time.time() - self._config.watchdog.display_log_timeout,
                                    "distanceAlert":time.time() - self._config.watchdog.display_log_timeout
                                    }
        self._connectionDownTime = 0
        self._lastConnection = time.time()
        self._distance = 0

        self._shouldBrake = self._config.watchdog.brake
        self._loggerTime = 0

        self._electricStats = {'underVoltageLevel': 0,
                                    'overVoltageLevel': 0,
                                    'overCurrentLevel': 0,
                                    'batteryPercentageLevel': 0
                                    }
        self._pinHash = pinHash
        self._scan = False

    def systemShutdown(self):
        if self._config.watchdog.shutdown == True:
            logger.info("initiating safe shutdown")
            ### add functionality to cut power to motor controller
            logger.info("this connection will be lost")
            self._pinHash['motorRelay'].toggleOff()
            self._pinHash['laserRelay'].toggleOff()
            self._pinHash['ledRelay'].toggleOff()       
            subprocess.call(['sudo poweroff'], shell=True)
        else:
            logger.critical('shutdown functionality was disabled in settings')

    def watch(self, telemetry):
        self.check(telemetry)
        if self._enableWatchdog == True:
            self.bark()

        return self._electricStats
    
    def shouldDisplay(self,key):
        if ( time.time() - self._lastDisplayTime[key] ) > self._config.watchdog.display_log_timeout:
            self._lastDisplayTime[key] = time.time()
            return True
        else:
            return False

    def betweenRange(self,value,lower,upper):
        if value > lower and value < upper:
            return True
        else:
            return False


    def check(self, telemetry):
        sysV = telemetry['SystemVoltage']
        sysI = telemetry['SystemCurrent']
        sensorDistance = telemetry['SensorDistance']
        connectionStatus = telemetry['Ping']
        self.checkOverCurrent(sysI)
        self.checkOverVoltage(sysV)
        self.checkUnderVoltage(sysV)
        self.checkDistance(sensorDistance)
        self.checkConnection(connectionStatus)

    def bark(self):
        self.barkAtOverVoltage()
        self.barkAtUnderVoltage()
        self.barkAtOverCurrent()
        self.barkAtBattPercent()
        self.barkAtDistance()
        if all(value == 0 for value in self._electricStats.values()) == True:
            self._pinHash['warningLED'].toggleOff() # turning off warning LED if all values == 0

    def checkOverVoltage(self, sysV):
        # testing for overVoltage
        alert = self._levels.over_voltage_alert
        warning = self._levels.over_voltage_warning
        critical = self._levels.over_voltage_critical

        if sysV > critical:
            self._electricStats['overVoltageLevel'] = 3  # overVoltage is at critical level
        elif betweenRange(sysV,warning,critical):
            self._electricStats['overVoltageLevel'] = 2  # overVoltage is at warning level
        elif betweenRange(sysV,alert,warning):
            self._electricStats['overVoltageLevel'] = 1  # overVoltage is at alert level
        elif sysV < alert:
            self._electricStats['overVoltageLevel'] = 0

    def checkUnderVoltage(self, sysV):
        # testing for underVoltage
        alert = self._levels.under_voltage_alert
        warning = self._levels.under_voltage_warning
        critical = self._levels.under_voltage_critical

        if sysV < critical:
            self._electricStats['underVoltageLevel'] = 3  # underVoltage is at critical level
        elif betweenRange(sysV,critical,warning):
            self._electricStats['underVoltageLevel'] = 2  # underVoltage is at warning level
        elif betweenRange(sysV,warning,alert):
            self._electricStats['underVoltageLevel'] = 1  # underVoltage is at alert level
        elif sysV > alert:
            self._electricStats['underVoltageLevel'] = 0
            
        #<crit
        #<warn,>crit
        #<alert,>warn
        #>alert

    def checkOverCurrent(self, sysI):
        # testing for overCurrent
        if sysI > self._levels.over_current_critical:
            self._electricStats['overCurrentLevel'] = 3  # overCurrent is at critical level
        elif sysI > self._levels.over_current_warning and sysI < self._levels.over_current_critical:
            self._electricStats['overCurrentLevel'] = 2  # overCurrent is at warning level
        elif sysI > self._levels.over_current_alert and sysI < self._levels.over_current_warning:
            self._electricStats['overCurrentLevel'] = 1  # overCurrent is at alert level
        elif sysI < self._levels.over_current_alert:
            self._electricStats['overCurrentLevel'] = 0

    def checkBatteryPercentage(self, batt):
        # testing for batteryPercentage
        if batt < self._levels.batt_percent_critical:
            self._electricStats['batteryPercentageLevel'] = 3  # batteryPercentage is at critical level
        elif batt < self._levels.batt_percent_warning and batt > self._levels.batt_percent_critical:
            self._electricStats['batteryPercentageLevel'] = 2  # batteryPercentage is at warning level
        elif batt < self._levels.batt_percent_alert and batt > self._levels.batt_percent_warning:
            self._electricStats['batteryPercentageLevel'] = 1  # batteryPercentage is at alert level
        elif batt > self._levels.batt_percent_alert:
            self._electricStats['batteryPercentageLevel'] = 0

    def checkDistance(self, sensorDistance):
        formatDistance = sensorDistance.replace('\r', '').replace('\n', '')
        if formatDistance == 'out of range' or float(formatDistance) < 0.0:
            self._distance = self._levels.distance_alert
        else:
            self._distance = float(formatDistance)

    def checkConnection(self, connectionStatus):
        if connectionStatus != -1:
            self._connectionDownTime = 0
            self._lastConnection = time.time()
        else:
            self._connectionDownTime = time.time() - self._lastConnection


    def barkAtBattPercent(self):
        value = self._electricStats['batteryPercentageLevel']
        shouldDisplay = self.shouldDisplay("batteryPercentage")

        if value in (1, 2, 3):
            self._pinHash['batteryLED'].toggleOn()
            if shouldDisplay:
                logger.critical("battery level at warning level" + str(value))

        if value == 3:
            if shouldDisplay:
                logger.critical("recommend initiating recall")

        elif value == 2:
            if shouldDisplay:
                logger.critical("recommend ending run soon")

        elif value == 1:
            if shouldDisplay:
                logger.warning("battery level at warning level 1")


    def barkAtOverCurrent(self):
        value = self._electricStats['overCurrentLevel']
        shouldDisplay = self.shouldDisplay("batteryPercentage")

        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            if shouldDisplay:
                logger.critical("overCurrent at warning level " + str(value))

        if value == 2:
            if shouldDisplay:
                logger.critical("current draw is much higher than expected")

        elif value == 3:
            if shouldDisplay:
                logger.critical("too much current detected! Recommend SHUTDOWN")

    def barkAtUnderVoltage(self):
        value = self._electricStats['underVoltageLevel']
        shouldDisplay = self.shouldDisplay("underVoltage")

        if value in (1, 2, 3):
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['batteryLED'].toggleOn()
            if shouldDisplay == True:
                logger.critical("underVoltage warning at level " + str(value))

        if value == 3:
            if shouldDisplay:
                logger.critical("battery Voltage too low -- reccomend emergency shutdown")
            if self._config.watchdog.shutdown == True:
                logger.critical("initiating emergency shutdown")
                self.systemShutdown()

        elif value == 2:
            if shouldDisplay:
                logger.critical('battery may be near death!')
                logger.critical('initating recall!')
            self.recall()

        elif value == 1:
            if shouldDisplay:
                logger.warning("battery may be close to dying, please check")

    def scanEnable(self):
        self._scan = True
    
    def scanDisable(self):
        self._scan = False
 
    def barkAtDistance(self):
        shouldDisplay = self.shouldDisplay("distanceAlert")
        if self._distance < 0.0:
            self._distance = "out of range"

        if isinstance(self._distance,str) == False: #distance check only occurs if distance is in range (not a string == "out of range")
            if self._distance <= self._levels.distance_alert and self._distance > self._levels.distance_warning:
                if shouldDisplay:
                    logger.warning("Distance at alert level")
            elif self._distance <= self._levels.distance_warning and self._distance > self._levels.distance_critical:
                if shouldDisplay:
                    logger.critical("Distance at warning level")
            elif self._distance <= self._levels.distance_critical:
                if shouldDisplay:
                    logger.critical("Distance at Critical Levels")
                if self._scan == True:
                    #recall instead
                    if shouldDisplay:
                        logger.critical("Scan enabled, recalling mars")
                    self.recall()
                else:
                    self.brake()
                    if shouldDisplay:
                        logger.warning("Brake has been enabled")

    def barkAtOverVoltage(self):
        value = self._electricStats['overVoltageLevel']
        shouldDisplay = self.shouldDisplay("overVoltage")
        
        # OVERVOLTAGE
        if value == 3:
            self._pinHash['warningLED'].toggleOn()
            self._pinHash['motorRelay'].toggleOff()
            self._pinHash['ledRelay'].toggleOff()
            self._pinHash['laserRelay'].toggleOff()
            self._pinHash['relay4'].toggleOff()

            if shouldDisplay == True:
                logger.critical("overVoltage warning at level 3")
                logger.critical("motor, LEDs, and laser circuits turned off")
                logger.critical("recommend disabling watchdog and recalling mars")

        elif value == 2:
            self.recall()
            self._pinHash['warningLED'].toggleOn()
            if shouldDisplay == True:
                logger.critical("overVoltage at warning level 2")
                logger.critical("recommend enabling a recall")

        elif value == 1:
            self._pinHash['warningLED'].toggleOn()
            if shouldDisplay == True:
                logger.warning("overVoltage at warning level 1")
                logger.warning("recommend checking power supply")

    def barkAtConnection(self):
        if self._connectionDownTime >= self._levels.connection_timeout:
            self.recall()

    def recall(self):
        # tell mars to head backwards toward operator
        if self._config.watchdog.recall_enabled == True:
            self._arduino.write(self._levels.recall_code)
            logger.critical("recall initiated")
            logger.critical("type 'watchdog off' to resume control")
        else:
            if shouldDisplay:
                logger.critical('recall was not initiated b/c settings.json specified so')


    def brake(self):
        if self._config.watchdog.brake == True:
            self._arduino.write(self._config.watchdog.brake_code)

    def disable(self):
        if self._enableWatchdog == False:
            logger.warning("watchdog is already disabled")
        else:
            self._enableWatchdog = True
            logger.critical("watchdog disabled")

    def enable(self):
        if self._enableWatchdog == True:
            logger.warning("watchdog is already enabled")
        else:
            self._enableWatchdog = True
            logger.critical("watchdog enabled")


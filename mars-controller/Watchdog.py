import logging
import time

class Watchdog(object):
    def __init__(self, jetson):
        self._jetson = jetson
        self._config = jetson._config

        self._enableWatchdog = self._levels.enableWatchdog
        self._levels = jetson._config.watchdog
        self._displayLogTimeout = self._levels.displayLogTimeout

        self._shouldBrake = 0
        self._loggingTime = 0

        self._shouldDisplay = {"underVoltage":True,"overVoltage":True,"batteryPercentage":True,"overCurrent":True}
        self._electricStatistics = {'underVoltageLevel': 0, 'overVoltageLevel': 0, 'overCurrentLevel': 0,
                                    'batteryPercentageLevel': 0}


    def watch(self):
        self.sniff()
        if self._enableWatchdog == True:
            waitTime = time.time() - self._loggingTime
            if waitTime > self._displayLogTimeout:
                self._shouldDisplay = self._shouldDisplay.fromkeys(self._shouldDisplay.iterkeys(), True)
                self._loggingTime = time.time()
            self.bark()

    def sniff(self):

        sysV = self._jetson._mars._statistics['SystemVoltage']
        sysI = self._jetson._mars._statistics['SystemCurrent']
        frontDistance = self._jetson._mars._statistics['frontDistance']
        backDistance = self._jetson._mars._statistics['backDistance']

        self.sniffOverCurrent(sysI)
        self.sniffOverVoltage(sysV)
        self.sniffUnderVoltage(sysV)
        self.sniffDistance(frontDistance, backDistance)

    def bark(self):
        self.barkAtOverVoltage()
        self.barkAtUnderVoltage()
        self.barkAtOverCurrent()
        self.barkAtBattPercent()
        if all(value == 0 for value in self._electricStatistics.values()) == True:
            self._jetson._turnOffComponent('warningLED')  # turning off warning LED if all values == 0

    def sniffOverVoltage(self, sysV):
        # testing for overVoltage
        if sysV > self._levels.overVoltageCritical:
            self._electricStatistics['overVoltageLevel'] = 3  # overVoltage is at critical level
        elif sysV > self._levels.overVoltageWarning and sysV < self._levels.overVoltageCritical:
            self._electricStatistics['overVoltageLevel'] = 2  # overVoltage is at warning level
        elif sysV > self._levels.overVoltageAlert and sysV < self._levels.overVoltageWarning:
            self._electricStatistics['overVoltageLevel'] = 1  # overVoltage is at alert level
        elif sysV < self._levels._overVoltageAlert:
            self._electricStatistics['overVoltageLevel'] = 0

    def sniffUnderVoltage(self, sysV):
        # testing for underVoltage
        if sysV < self._levels.underVoltageCritical:
            self._electricStatistics['underVoltageLevel'] = 3  # underVoltage is at critical level
        elif sysV < self._levels.underVoltageWarning and sysV > self._levels.underVoltageCritical:
            self._electricStatistics['underVoltageLevel'] = 2  # underVoltage is at warning level
        elif sysV < self._levels.underVoltageAlert and sysV > self._levels.underVoltageWarning:
            self._electricStatistics['underVoltageLevel'] = 1  # underVoltage is at alert level
        elif sysV > self._levels.underVoltageAlert:
            self._electricStatistics['underVoltageLevel'] = 0

    def sniffOverCurrent(self, sysI):
        # testing for overCurrent
        if sysI > self._levels.overCurrentCritical:
            self._electricStatistics['overCurrentLevel'] = 3  # overCurrent is at critical level
        elif sysI > self._levels.overCurrentWarning and sysI < self._levels.overCurrentCritical:
            self._electricStatistics['overCurrentLevel'] = 2  # overCurrent is at warning level
        elif sysI > self._levels.overCurrentAlert and sysI < self._levels.overCurrentWarning:
            self._electricStatistics['overCurrentLevel'] = 1  # overCurrent is at alert level
        elif sysI < self._levels._overCurrentAlert:
            self._electricStatistics['overCurrentLevel'] = 0

    def sniffBatteryPercentage(self, batt):
        # testing for batteryPercentage
        if batt < self._levels.battPercentCritical:
            self._electricStatistics['batteryPercentageLevel'] = 3  # batteryPercentage is at critical level
        elif batt < self._levels.battPercentWarning and batt > self._levels.battPercentCritical:
            self._electricStatistics['batteryPercentageLevel'] = 2  # batteryPercentage is at warning level
        elif batt < self._levels.battPercentAlert and batt > self._levels.battPercentWarning:
            self._electricStatistics['batteryPercentageLevel'] = 1  # batteryPercentage is at alert level
        elif batt > self._levels.battPercentAlert:
            self._electricStatistics['batteryPercentageLevel'] = 0

    def sniffDistance(self, frontDistance, backDistance):
        distanceList = [frontDistance, backDistance]
        if frontDistance == 'out of range' and backDistance == 'out of range':
            self._shouldBrake = 0
        else:
            distanceList = filter(lambda a: a != 'out of range', distanceList)
            if min(distanceList) < self._levels.brakingDistance:
                self._shouldBrake = 1



    def barkAtBattPercent(self):
        value = self._electricStatistics['batteryPercentageLevel']
        display = self._shouldDisplay["batteryPercentage"]
        if value == 3:
            self._jetson._turnOnComponent('batteryLED')
            if display == True:
                logging.critical("battery level at warning level 3")
                logging.critical("recommend initiating recall")
        if value == 2:
            self._jetson._turnOnComponent('batteryLED')
            if display == True:
                logging.critical("battery level at warning level 2")
                logging.critical("recommend ending run soon")
        if value == 1:
            self._jetson._turnOnComponent('batteryLED')
            if display == True:
                logging.warning("battery level at warning level 1")


    def barkAtOverCurrent(self):
        value = self._electricStatistics['overCurrentLevel']
        display = self._shouldDisplay["overCurrent"]
        if value == 3:
            self._jetson._turnOnComponent('warningLED')
            if display == True:
                logging.critical("overCurrent at warning level 3")
                logging.critical("too much current detected! Recommend SHUTDOWN")
        if value == 2:
            self._jetson._turnOnComponent('warningLED')
            if display == True:
                logging.critical("overCurrent at warning level 2")
                logging.critical("current draw is much higher than expected")
        if value == 1:
            self._jetson._turnOnComponent('warningLED')
            if display == True:
                logging.warning("overCurrent at warning level 1")


    def barkAtUnderVoltage(self):
        value = self._electricStatistics['underVoltageLevel']
        if value == 3:
            self._jetson._turnOnComponent('warningLED')
            self._jetson._turnOnComponent('batteryLED')
            if self._shouldDisplay["underVoltage"] == True:
                logging.critical("underVoltage warning at level 3")
                logging.critical("initiating emergency shutdown")
                self._shouldDisplay['underVoltage'] = False
            self._jetson.systemShutdown()
        elif value == 2:
            self._jetson._turnOnComponent('warningLED')
            self._jetson._turnOnComponent('batteryLED')
            if self._shouldDisplay["underVoltage"] == True:
                logging.critical("underVoltage warning at level 2")
                logging.critical('battery may be near death!')
                self._shouldDisplay['underVoltage'] = False
        elif value == 1:
            self._jetson._turnOnComponent('warningLED')
            self._jetson._turnOnComponent('batteryLED')
            if self._shouldDisplay["underVoltage"] == True:
                logging.warning("underVoltage warning at level 1")
                logging.warning("battery may be close to dying, please check")
                self._shouldDisplay['underVoltage'] = False


    def barkAtOverVoltage(self):
        value = self._electricStatistics['overVoltageLevel']
        # OVERVOLTAGE
        if value == 3:
            self._jetson._turnOnComponent('warningLED')
            self._jetson._turnOffComponent('motorRelay')
            self._jetson._turnOffComponent('ledRelay')
            self._jetson._turnOffComponent('laserRelay')
            self._jetson._turnOffComponent('relay4')
            if self._shouldDisplay['overVoltage'] == True:
                logging.critical("overVoltage warning at level 3")
                logging.critical("motor, LEDs, and laser circuits turned off")
                logging.critical("recommend disabling watchdog and recalling mars")
        elif value == 2:
            self.recall()
            self._jetson._turnOnComponent('warningLED')
            if self._shouldDisplay['overVoltage'] == True:
                logging.critical("overVoltage at warning level 2")
                logging.critical("recommend enabling a recall")
        elif value == 1:
            self._jetson._turnOnComponent('warningLED')
            if self._shouldDisplay['overVoltage'] == True:
                logging.warning("overVoltage at warning level 1")
                logging.warning("recommend checking power supply")


    def recall(self):
        # tell mars to head backwards toward operator
        self._jetson._arduino.write(self._levels.recallCode)
        logging.critical("recall initiated")
        logging.critical("type 'disable watchdog' to resume control")


    def disable(self):
        if self._enableWatchdog == False:
            logging.warning("watchdog is already disabled")
        else:
            self._enableWatchdog = True
            logging.critical("watchdog disabled")


    def enable(self):
        if self._enableWatchdog == True:
            logging.warning("watchdog is already enabled")
        else:
            self._enableWatchdog = True
            logging.critical("watchdog enabled")

import logging


class Watchdog(object):
    def __init__(self, jetson):
        self._jetson = jetson
        self._config = jetson._config

        self._electricStatistics = {'underVoltageLevel': 0, 'overVoltageLevel': 0, 'overCurrentLevel': 0, 'batteryPercentageLevel': 0}

        self._shouldBrake = 0
        self._levels = jetson._config.watchdog
        self._enableWatchdog = self._levels.enableWatchdog

    def watch(self):
        self.sniff()
        if self._enableWatchdog == True:
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
        pass

    def barkAtOverCurrent(self):
        pass

    def barkAtUnderVoltage(self):
        value = self._electricStatistics['underVoltageLevel']
        if value == 3:
            self._jetson._turnOnComponent('warningLED')
            logging.critical("battery voltage is at critical levels")
            logging.critical("currently at {0}volts, warning level is {1}volts" \
                             .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.underVoltageWarning))
            logging.critical("battery percentage indicator may be wrong!")
            logging.critical("initating sys-shutdown")
            self._jetson.systemShutdown()
        elif value == 2:
            self._jetson._turnOnComponent('warningLED')
            logging.critical("battery voltage is getting low")
            logging.critical("currently at {0}volts, warning level is {1}volts" \
                             .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.underVoltageWarning))
            logging.critical("battery percentage indicator may be wrong!")
            logging.critical(
                "if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
        elif value == 1:
            self._jetson._turnOnComponent('warningLED')
            logging.warning("battery voltage is getting low")
            logging.warning("currently at {0}volts, warning level is {1}volts" \
                            .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.underVoltageWarning))
            logging.warning("battery percentage indicator may be wrong!")
            logging.warning(
                "if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")

    def barkAtOverVoltage(self):
        value = self._electricStatistics['overVoltageLevel']
        # OVERVOLTAGE
        if value == 3:
            self._jetson._turnOnComponent('warningLED')
            self._jetson._turnOffComponent('motorRelay')
            self._jetson._turnOffComponent('ledRelay')
            self._jetson._turnOffComponent('laserRelay')
            self._jetson._turnOffComponent('relay4')
            logging.critical("supply voltage is too high, components are at risk of being damaged")
            logging.critical("currently at {0}volts, expected less than {1}volts" \
                             .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.overVoltageAlert))
            logging.critical("all components have been turned off")
            logging.critical("voltage sensor failure is probable cause")
            logging.critical(
                "if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
        elif value == 2:
            self.recall()
            self._jetson._turnOnComponent('warningLED')
            logging.critical("supply voltage is much higher than usual")
            logging.critical("currently at {0}volts, expected less than {1}volts"\
                             .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.overVoltageAlert))
            logging.critical("recalling Mars for inspection")
            logging.critical("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
        elif value == 1:
            self._jetson._turnOnComponent('warningLED')
            logging.warning("Voltage is higher than expected")
            logging.warning("currently at {0}volts, expected less than {1}volts" \
                            .format(self._jetson._mars._statistics['SystemVoltage'], self._levels.overVoltageAlert))
            logging.warning(
                "if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")

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

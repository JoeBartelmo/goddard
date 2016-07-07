import logging


class Watchdog(object):
    def __init__(self, jetson):
        self._jetson = jetson
        self._config = jetson._config
        self._electricStatistics = {'underVoltage': 0, 'overVoltage': 0, 'overCurrent': 0}
        self._distanceFromObject = {'front': None, 'back': None}  # for when distance sensors are added


    def sniffPower(self):
        """
        this method 'sniffs' the telemetry data of Mars and checks to see if it is within a normal range

            this modifies the self._electricStatistics attribute which indicates the severity of the problem.
            0 is nominal, 1 is Alert level (alerts the operator), 2 is warning level (triggers a recall)
            3 is critical level (triggers a shutdown)

        (currently this checks for under-voltage,over-voltage and over-current. However, this will most certainly be expanded
        once I implement distance sensing.)

        """

        sysV = self._jetson._mars._statistics['SystemVoltage']
        sysI = self._jetson._mars._statistics['SystemCurrent']
        levels = self._config.constants

        self.testOverCurrent(sysI, levels)
        self.testOverVoltage(sysV, levels)
        self.testUnderVoltage(sysV, levels)

        return self._electricStatistics

    def testOverVoltage(self, sysV, levels):
        #testing for overVoltage
        if sysV > levels.overVoltageCritical:
            self._electricStatistics['overVoltage'] = 3 #overVoltage is at critical level
            logging.critical("SUPPLY VOLTAGE IS ABOVE CRTICAL LEVELS")
        elif sysV in range(levels.overVoltageWarning,levels.overVoltageCritical):
            self._electricStatistics['overVoltage'] = 2 #overVoltage is at warning level
            logging.warning("supply voltage is above recommended levels, damage to components may occur")
        elif sysV in range(levels.overVoltageAlert,levels.overVoltageWarning):
            self._electricStatistics['overVoltage'] = 1 #overVoltage is at alert level
            logging.info("voltage is higher than usual, recommend checking power source and VRM")
        elif sysV < levels._overVoltageAlert:
            self._electricStatistics['overVoltage'] = 0
            logging.info("")

    def testUnderVoltage(self, sysV, levels):
        #testing for underVoltage
        if sysV < levels.underVoltageCritical:
            self._electricStatistics['underVoltage'] = 3 #underVoltage is at critical level
            logging.critical("SUPPLY VOLTAGE IS CRITIALLY LOW, HIGH RISK OF DAMAGE TO BATTERIES")
        elif sysV in range(levels.underVoltageWarning,levels.underVoltageCritical):
            self._electricStatistics['underVoltage'] = 2 #underVoltage is at warning level
        elif sysV in range(levels.underVoltageAlert,levels.underVoltageWarning):
            self._electricStatistics['underVoltage'] = 1 #underVoltage is at alert level
            logging.warning("Supply Voltage extremely low, BATTERIES MAY BE CLOSE TO DEATH ")
        elif sysV > levels.underVoltageAlert:
            self._electricStatistics['underVoltage'] = 0
            logging.info("battery voltage is too low, recommend ending run soon")

    def testOverCurrent(self, sysI, levels):
        #testing for overCurrent
        if sysI > levels.overCurrentCritical:
            self._electricStatistics['overCurrent'] = 3 #overCurrent is at critical level
            logging.critical("SYSTEM CURRENT IS TOO HIGH. MARS MAY BE SAFETY HAZARD")
        elif sysI in range(levels.overCurrentWarning,levels.overCurrentCritical):
            self._electricStatistics['overCurrent'] = 2 #overCurrent is at warning level
            logging.warning("Mars is pulling too much current and is at risk of being a safety hazard")
        elif sysI in range(levels.overCurrentAlert,levels.overCurrentWarning):
            self._electricStatistics['overCurrent'] = 1 #overCurrent is at alert level
            logging.info("Mars is pulling more current than usual. Recommend checking over components for any possible problems")
        elif sysI < levels._overCurrentAlert:
            self._electricStatistics['overCurrent'] = 0

    def sniffUltrasonicDistance(self):
        return self._distanceFromObject


    def react(self):
        if 3 in self._electricStatistics.values():
            self._jetson.system_shutdown()
        elif 2 in self._electricStatistics.values():
            self._jetson.mars.recall()

        #engaging the brake if we are too close to an object
        frontDistance = self._distanceFromObject['front']
        backDistance = self._distanceFromObject['back']
        brakingDistance = self._config.constants.brakingDistance

        if frontDistance != 'out of range':
            if backDistance < brakingDistance:
                logging.warning("object obstructing path detected. \r\n Engaging brake")
                self._jetson._arduino.brake() #the control code to brake Mars


        if backDistance != 'out of range':
            if backDistance < brakingDistance:
                logging.warning("object obstructing path detected. \r\n Engaging brake")
                self._jetson._arduino.brake() #the control code to brake Mars








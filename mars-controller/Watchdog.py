import logging


class Watchdog(object):
     def __init__(self, jetson):
         self._jetson = jetson
         self._config = jetson._config
         self._enableWatchdog = False
         self._electricStatistics = {'underVoltage': 0, 'overVoltage': 0, 'overCurrent': 0, 'batteryPercentage':0}
         self._shouldBrake = 0
         self._levels = jetson._config.watchdog
 
 
     def watch(self):
         if self._enableWatchdog == True:
             self.sniff()
             self.react()
 
     def sniff(self):
 
         sysV = self._jetson._mars._statistics['SystemVoltage']
         sysI = self._jetson._mars._statistics['SystemCurrent']
         frontDistance = self._jetson._mars._statistics['frontDistance']
         backDistance = self._jetson._mars._statistics['backDistance']
 
         self.testOverCurrent(sysI)
         self.testOverVoltage(sysV)
         self.testUnderVoltage(sysV)
         self.testDistance(frontDistance,backDistance)
 
 
     def testOverVoltage(self, sysV):
         #testing for overVoltage
         if sysV > self._levels.overVoltageCritical:
             self._electricStatistics['overVoltage'] = 3 #overVoltage is at critical level
         elif sysV > self._levels.overVoltageWarning and sysV < self._levels.overVoltageCritical:
             self._electricStatistics['overVoltage'] = 2 #overVoltage is at warning level
         elif sysV > self._levels.overVoltageAlert and sysV < self._levels.overVoltageWarning:
             self._electricStatistics['overVoltage'] = 1 #overVoltage is at alert level
         elif sysV < self._levels._overVoltageAlert:
             self._electricStatistics['overVoltage'] = 0
 
     def testUnderVoltage(self, sysV):
         #testing for underVoltage
         if sysV < self._levels.underVoltageCritical:
             self._electricStatistics['underVoltage'] = 3 #underVoltage is at critical level
         elif sysV < self._levels.underVoltageWarning and sysV > self._levels.underVoltageCritical:
             self._electricStatistics['underVoltage'] = 2 #underVoltage is at warning level
         elif sysV < self._levels.underVoltageAlert and sysV > self._levels.underVoltageWarning:
             self._electricStatistics['underVoltage'] = 1 #underVoltage is at alert level
         elif sysV > self._levels.underVoltageAlert:
             self._electricStatistics['underVoltage'] = 0
 
 
     def testOverCurrent(self, sysI):
         #testing for overCurrent
         if sysI > self._levels.overCurrentCritical:
             self._electricStatistics['overCurrent'] = 3 #overCurrent is at critical level
         elif sysI > self._levels.overCurrentWarning and sysI < self._levels.overCurrentCritical:
             self._electricStatistics['overCurrent'] = 2 #overCurrent is at warning level
         elif sysI > self._levels.overCurrentAlert and sysI < self._levels.overCurrentWarning:
             self._electricStatistics['overCurrent'] = 1 #overCurrent is at alert level
         elif sysI < self._levels._overCurrentAlert:
             self._electricStatistics['overCurrent'] = 0
 
     def testBatteryPercentage(self,batt):
          #testing for batteryPercentage
         if batt < self._levels.battPercentCritical:
             self._electricStatistics['batteryPercentage'] = 3 #batteryPercentage is at critical level
         elif batt < self._levels.battPercentWarning and batt > self._levels.battPercentCritical:
             self._electricStatistics['batteryPercentage'] = 2 #batteryPercentage is at warning level
         elif batt < self._levels.battPercentAlert and batt > self._levels.battPercentWarning:
             self._electricStatistics['batteryPercentage'] = 1 #batteryPercentage is at alert level
         elif batt > self._levels.battPercentAlert:
             self._electricStatistics['batteryPercentage'] = 0
 
     def testDistance(self,frontDistance,backDistance):
         distanceList = [frontDistance,backDistance]
         if frontDistance == 'out of range' and backDistance == 'out of range':
             self._shouldBrake = 0
         else:
             distanceList = filter(lambda a: a != 'out of range', distanceList)
             if min(distanceList) < self._levels.brakingDistance:
                 self._shouldBrake = 1
 
 
     def react(self):
         self.reactToOverVoltage()
         self.reactToUnderVoltage()
         self.reactToOverCurrent()
         self.reactToBattPercent()
         if all(value == 0 for value in self._electricStatistics.values()) == True:
             self._jetson._turnOffComponent('warningLED') #turning off warning LED if all values == 0
 
     def reactToBattPercent(self):
         pass
 
     def reactToOverCurrent(self):
         pass
 
 
     def reactToUnderVoltage(self):
         value = self._electricStatistics['underVoltage']
         if value == 3:
             self._jetson._turnOnComponent('warningLED')
             logging.critical("battery voltage is at critical levels")
             logging.critical("currently at {0}volts, warning level is {1}volts"\
                 .format(self._jetson._mars._statistics['SystemVoltage'],self._levels.underVoltageWarning))
             logging.critical("battery percentage indicator may be wrong!")
             logging.critical("initating sysshutdown")
             self._jetson.systemShutdown()
         elif value == 2:
             self._jetson._turnOnComponent('warningLED')
             logging.critical("battery voltage is getting low")
             logging.critical("currently at {0}volts, warning level is {1}volts"\
                 .format(self._jetson._mars._statistics['SystemVoltage'],self._levels.underVoltageWarning))
             logging.critical("battery percentage indicator may be wrong!")
             logging.critical("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
         elif value == 1:
             self._jetson._turnOnComponent('warningLED')
             logging.warning("battery voltage is getting low")
             logging.warning("currently at {0}volts, warning level is {1}volts"\
                 .format(self._jetson._mars._statistics['SystemVoltage'],self._levels.underVoltageWarning))
             logging.warning("battery percentage indicator may be wrong!")
             logging.warning("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
 
 
     def reactToOverVoltage(self):
         value = self._electricStatistics['overVoltage']
     #OVERVOLTAGE
         if value == 3:
             self._jetson._turnOnComponent('warningLED')
             self._jetson._turnOffComponent('motorRelay')
             self._jetson._turnOffComponent('ledRelay')
             self._jetson._turnOffComponent('laserRelay')
             self._jetson._turnOffComponent('relay4')
             logging.critical("supply voltage is too high, components are at risk of being damaged")
             logging.critical("currently at {0}volts, expected less than {1}volts"\
                 .format(self._jetson._mars._statistics['SystemVoltage'],self._levels.overVoltageAlert))
             logging.critical("all components have been turned off")
             logging.critical("voltage sensor failure is probable cause")
             logging.critical("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
         elif value == 2:
             self._jetson.mars.recall()
             self._jetson._turnOnComponent('warningLED')
             logging.critical("supply voltage is much higher than usual")
             logging.critical("currently at {0}volts, expected less than {1}volts")
             logging.critical("recalling Mars for inspection")
             logging.critical("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
         elif value == 1:
             self._jetson._turnOnComponent('warningLED')
             logging.warning("Voltage is higher than expected")
             logging.warning("currently at {0}volts, expected less than {1}volts"\
                 .format(self._jetson._mars._statistics['SystemVoltage'],self._levels.overCurrentAlert))
             logging.warning("if you would like to disable automatic monitoring type 'disable watchdog' (NOT RECCOMENDED)")
 
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







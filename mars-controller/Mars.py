'''
ark9719
6/17/2016
'''
import re
import time
import logging
import sys

class Mars(object):
    """
    Mars is in control of pulling data from the arduino and generating relevant telemetry statistics. This includes
    stats on time, battery, distance, power, and more.
    """

    def __init__(self, arduino, config):
        self._arduino = arduino
        self._config = config
        self._integTime = time.time()
        self._currentBattery = self._config.constants.totalBattery

        statistics = {}
        self._statistics = statistics
        statistics.setdefault('distanceTraveled', 0)
        statistics.setdefault('distance', 0)
        statistics.setdefault('displacement', 0)
        statistics.setdefault('totalDisplacement', 0)
        statistics.setdefault('batteryRemaining', self._config.battery.remaining)


    def serial_readline(self):
        """
        This method manages pulling the raw data off the arduino.
        :return:
        """
        if (self._arduino._init == False):
            print("Arduino has not been initialized!")

        waitStart = time.time()
        waitTime = time.time() - waitStart
        timeout = self._config.constants.timeout

        while self._arduino._controller.inWaiting() == 0:
            if waitTime < timeout:
                waitTime =  time.time() - waitStart
            elif waitTime >= timeout:
                logging.info("no data coming from arduino before timeout")
                logging.info("ending program, check arduino or timeout duration")
                sys.exit()
        else:

            #added short delay just in case data was in transit
            time.sleep(.001)

            #read telemetry sent by Arduino
            serialData = self._arduino._controller.readline()

            #flushing in case there was a buildup
            self._arduino._controller.flushInput()

            return serialData



    def generateStatistics(self, integTime):
        """
        Through raw data and the work of helper functions, this method populates a dictionary stored attribute of Mars,
        statistics, with telemetry data.
        :param integTime:
        :return:
        """

        serialData = self.serial_readline()
        rawArray = re.split(",", serialData)

        #Assign integ time for use of helper functions
        copy = self._integTime
        currenttime = time.time()
        self._integTime = currenttime - copy

        print(rawArray)
        rpm = rawArray[0]
        self._statistics['rpm'] = rpm
        sysV = rawArray[1]
        self._statistics['sysV'] = sysV
        sysI = rawArray[2]
        sysI = sysI[0:len(sysI)-4]
        self._statistics['sysI'] = sysI

        speed = self.estimatedSpeed(rpm) #speed in m/s
        self._statistics['speed'] = speed
        power = self.estimatedPower(sysV, sysI) #power in Watts
        self._statistics['power'] = power


        distance, distanceTraveled = self.distanceTraveled(speed) #in Meters
        self._statistics['distance'] = distance
        self._statistics['distanceTraveled'] = distanceTraveled

        displacement, totalDisplacement = self.displacement(speed) #in Meters
        self._statistics['displacement'] = displacement
        self._statistics['totalDisplacement'] = totalDisplacement

        batteryRemaining = self.batteryRemaining(power)
        self._statistics['batteryRemaining'] = batteryRemaining



    def estimatedSpeed(self, rpm):
        """
        This function guesses how fast Mars is going based on the lastest RPM
        data from the DAQ.

        It does not take into account any other factors or forces, as a result
        this is an ESTIMATED SPEED, not a real speed

        this conversion is will only work for the current generation of MARS and
        is a function of this equation
            speed in mph ~= rpm/221
            speed in m/s ~= (rpm/221)*0.44704

        :param rpm:
        :return:
        """

        rpm = float(rpm) #rpm must be a float
        estMps = (rpm/221.0)*0.44704 #estimated SPEED in M/S

        returnEstMps = round(estMps, 1)
        self._currentSpeed = returnEstMps
        return returnEstMps

    def estimatedPower(self, sysVoltage, sysCurrent):
        """
        estimates the current power usage of mars based off of voltage and current data.
            P = V * I
        :param sysVoltage:
        :param sysCurrent:
        :return:
        """
        sysVoltage = float(sysVoltage)
        sysCurrent = float(sysCurrent)
        estPower = sysVoltage * sysCurrent

        powerReturned = round(estPower, 2)
        return powerReturned

    def distanceTraveled(self, speed, time=None):
        """
        returns the estimated distance traveled by mars. If the user feed this function a time parameter, then this will
        calculate the new distance based on the current speed and time given. Otherwise it will return the last
        calculated distance traveled by Mars.
        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDistance = abs(speed) * time
        travAdded = self._statistics['distanceTraveled'] + intervalDistance
        self._statistics['distanceTraveled'] = travAdded
        totalDistance = self._statistics['distanceTraveled']

        intervalDistanceRounded = round(intervalDistance,1)
        totalDistanceRounded = round(totalDistance, 1)

        return intervalDistanceRounded,totalDistanceRounded

    def displacement(self, speed, time=None):
        """

        :param speed:
        :param time:
        :return:
        """
        if time == None:
            time = self._integTime

        intervalDisplacement = speed * time
        self._statistics['displacement'] = self._statistics['displacement'] + intervalDisplacement
            # '--> updating the object attribute
        totalDisplacement = self._statistics['displacement']

        intervalDisplacement = round(intervalDisplacement,1) #Rounding for readability
        totalDisplacement = round(totalDisplacement, 1)

        return intervalDisplacement,totalDisplacement

    def batteryRemaining(self,power=None, time = None):
        """
        battery_remaining(power *optional*, time *optional*)::
        if the user inputs power or time data, then this function will calculate how much energy remains in the
        batteries. otherwise ths will return the last calculated battery status
        :param power:
        :param time:
        :return:
        """

        if time == None:
            time = self._integTime
        ########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########

        if power != None:

            print(power)
            print(time)
            joulesUsed  = float(power) * time
            print(joulesUsed)
            whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours
            print(whrUsed)

            self._currentBattery = float(self._currentBattery) - whrUsed
            #subtracting energy used from battery total

        battPercent = float(self._currentBattery) / float(self._config.constants.totalBattery) * 100.0
        battPercentReturned = round(battPercent, 1)

        return battPercentReturned


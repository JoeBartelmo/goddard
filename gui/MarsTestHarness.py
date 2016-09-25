from Queue import Queue
import random
import time

class MarsTestHarness(object):
    '''
    For use with GUI testing, will generate random data for each queue
    '''
    def __init__(self, telemetryQueue = None, beamGapQueue = None, refreshTime = 5):
        self._telemetryQueue = telemetryQueue
        self._beamGapQueue = beamGapQueue
        
        self._lastTime = time.time()
        self._refreshTime = refreshTime
        self._telemetry = {}

    def generateQueueData(self):
        '''
        Assigns randomized data to each queue
        '''
        if time.time() - self._lastTime >= self._refreshTime:
            if self._telemetryQueue is not None:
                self._telemetry['RunClock'] = time.time()
                self._telemetry['Ping'] = random.randint(10,100)

                self._telemetry['RPM'] = random.randint(100,1000)
                self._telemetry['SystemVoltage'] = random.randint(1,10)
                self._telemetry['SystemCurrent'] = random.randint(1,10)
                self._telemetry['SensorDistance'] = random.randint(0,100)

                self._telemetry['Speed'] = self._telemetry['RPM'] / 100
                self._telemetry['Power'] = self._telemetry['SystemVoltage'] * self._telemetry['SystemCurrent']

                self._telemetry['IntervalDistance'] = random.randint(0, 100)
                self._telemetry['TotalDistance'] = self._telemetry['IntervalDistnace'] * 2

                self._telemetry['IntervalDisplacement'] = self._telemetry['TotalDistance']
                self._telemetry['TotalDisplacement'] = self._telemetry['IntervalDisplacement']
                self._telemetry['BatteryRemaining'] = random.randint(0,100)

                #pulling in last commands
                self._telemetry['SetSpeed'] = random.randint(0,9)
                self._telemetry['LEDBrightness'] = random.randint(0,9)

                #pulling in the state of relays
                self._telemetry['MotorCircuit'] = random.randint(0,1)
                self._telemetry['LedCircuit'] =  random.randint(0,1)
                self._telemetry['LaserCircuit'] = random.randint(0,1)

                self._telemetryQueue.put(self._telemetry)
            if self._beamGapQueue is not None:
                beamGapLength = random.randint(10, 100)
                beamGap = []
                previousRandValue = 10
                for i in range(0, beamGapLength):
                    previousRandValue += random.randint(-1, 1)
                    beamGap.push(previousRandValue)
                self._beamGapQueue.put(beamGap)
            self._lastTime = time.time()

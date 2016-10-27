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
import re
logger = logging.getLogger('mars_logging')

class LED(object):
    """
    An LED class representing the LED's attached to MARS. Currently, the only command modifies their brightness 0-9
    """

    def __init__(self):
        self._LEDcodes = ['brightness']
        self._lastCommand = 'L0'
        self._brightness = 0

    def issue(self, arduino, controlCode):
        """
        Issue an LED command. Store the data contained in the command an issue a write.
        :param arduino:
        :param controlCode:
        :return:
        """
        self._arduino = arduino
        splitCode = re.split(" ",controlCode)
        logger.info("preparing to issue LED command...")
        if len(splitCode) == 2 and 'brightness' == splitCode[0] and RepresentsInt(splitCode[1]):
            self._brightness = splitCode[1] 
            logger.info("command issued to LEDs")
            self.write()

    def write(self):
        """
        Write the last stored command to the arduino
        :return:
        """
        command = 'L' + str(self._brightness)
        self._arduino.write('L' + str(self._brightness))
        self._lastCommand = command
        logger.info('writing LED code {0} to arduino '.format(command))

class Motor(object):
    """
    A class representing the motor attached to MARS. Contains all relevant directional, speed and motor data.
    """

    def __init__(self):
        self._motorCodes = ['brake on', 'brake off', 'motor on', 'motor off']
        self._speed = 0
        self._lastCommand = 'M0000'
        self._direction = 0
        self._brake = 0
        self._enabled = 0

    def issue(self, myCode, arduino):
        """
        Issue a motor command.
        :param myCode:
        :param arduino:
        :return:
        """
        self._arduino = arduino
        logger.info("preparing to issue motion command...")
        if myCode in ('motor on', 'motor off'):
            self.toggleMotor(myCode)
        elif myCode in ('brake on', 'brake off'):
            self.toggleBrake(myCode)


    def movement(self, myCode):
        """
        Decipher the type of movement command, store the values and call to the arduino.
        :param myCode:
        :return:
        """
        # uncomment if braking and enable check wanted
#         if self._enabled == 0:
#            return logger.info("Motor must be enabled before you can move! Use: motor on")
#         if self._brake == 1:
#            return logger.info("Brake must be disabled to move! Use: brake off")
        
        splitCodes = myCode.split(' ')

        if len(splitCodes) == 2 and RepresentsInt(splitCodes[1]):
            self._enabled = 1
            self._direction = 1 if 'forward' == splitCodes[0] else 0
            self._brake = 0
            self._speed = splitCodes[1]
            self.write()
            
        elif "brake" == splitCodes[0]:
            if len(splitCodes) == 2:
                self.toggleBrake(myCode)
            else:
                self.toggleBrake()
        else:
            return logger.warning("Speed must be 0-9. Direction must be forward or backward.")

    def toggleMotor(self, myCode):
        """
        Toggles the motor
        :param myCode:
        :return:
        """
        if myCode == 'motor on':
            self._enabled = 1
        elif myCode == 'motor off':
            self._enabled = 0

        self.write()

    def toggleBrake(self, myCode = None):
        """
        Toggles the brake
        :param myCode:
        :return:
        """
        if myCode == 'brake on':
            self._enabled = 0
            self._direction = 0
            self._brake = 1
            self._speed = 0
        elif myCode == 'brake off':
            self._brake = 0
        elif myCode is None:
            if self._brake == 0:
                self._brake = 1
            else:
                self._brake = 0
        else:
            return logger.warning("Invalid brake code. Should be 'brake on' or 'brake off'")

        self.write()

    def start(self):
        """
        Default motor configurations
        :return:
        """
        self._enabled = 0
        self._direction = 0
        self._brake = 1
        self._speed = 0

        self.write()

    #@depricated
    def brake(self):
        """
        Hard brake setting
        :return:
        """
        self.toggleBrake('brake on')

    def write(self):
        """
        Write respective motor command to the arduino
        :return:
        """
        command = 'M' + str(self._enabled) + str(self._direction) + str(self._brake) + str(self._speed)
        logger.info('writing motion code {0} to arduino '.format(command))
        self._lastCommand = command
        self._arduino.write(command)

def RepresentsInt(s):
    try:
        integ = int(s)
        if integ in range(10): 
            return True
    except Exception:
        logger.warning("input not integer or out of range [usually between 0 and 9]")
        return False


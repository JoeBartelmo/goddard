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
import os
"""

Usable GPIO pins are as follows

160,161,162,163,164,165,166,57

#EMBED ANY REFERENCE TO THIS IN A TRY STATEMENT
##ValueError will be generated if there is an invalid gpioPin



#MUST MODIFY WATCHDOG TO MONITOR AND CHANGE INDICATORS 

create 8 pin objects:

	reset pin (166)
	connection LED (163)
	warning LED (164)
	batt LED (165)
	relay 1 (57)
	relay 2 (160)
	relay 3 (161)
	relay 4 (162)


"""

logger = logging.getLogger('mars_logging')
gpio_list = [57,160,161,162,163,164,165,166]

class GpioPin(object):
    """
    Class representing the GPIO pins on board.
    """

    def __init__(self, gpioPin, direction = 'out'):
        self._state = 0
        self._direction = direction

        if gpioPin in gpio_list:
            self._gpioPin = gpioPin
        else:
            logger.warning("GPIO PIN SETUP FAILED\r\nGPIO pin {} does not exist".format(str(gpioPin)))
            logger.warning("GPIO pin must be one of the following {}".format(str(gpio_list)))
            raise ValueError("invalid GPIO pin number")


    def setup(self):
        """
        Set up the GPIO pin by exporting it and setting the direction
        :return:
        """
        #exporting the GPIO pin so it can be accessed
        with open('/sys/class/gpio/export','w') as export_file:
            if not os.path.exists('/sys/class/gpio/export/gpio' + str(self._gpioPin)):
                export_file.write(str(self._gpioPin))
        #setting the pin direction
        with open('/sys/class/gpio/gpio{}/direction'.format(str(self._gpioPin)),'w') as direction_file:
            direction_file.write(self._direction)


    def changeState(self,state):
        """
        Change the state of the GPIO pin to the passed in state
        :param state: The state of the pin provided by the user
        :return:
        """
        logger.debug('Writing ' + str(state) + ' to pin ' + str(self._gpioPin))
        if self._direction == "out":
            with open('/sys/class/gpio/gpio{}/value'.format(str(self._gpioPin)),'w') as value_file:
                value_file.write(str(state))
        else:
            logger.critical('Pin (' + self._gpioPin + ') must be an output to change its state')

        self._state = state

    def toggleOn(self):
        """
        Toggle the GPIO pin on (1)
        :return:
        """
        self.changeState(1)

    def toggleOff(self):
        """
        Toggle the GPIO pin off (0)
        :return:
        """
        self.changeState(0)


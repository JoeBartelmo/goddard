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
import subprocess

logger = logging.getLogger('mars_logging')

class Stream (object):

    def __init__(self, config, timestamp):
        self._streamCodes = ['low res stream', 'high res stream']
        self._config = config
        self._bitrate = 'None yet'
        self._resolution = 'None yet'
        self._timestamp = timestamp
        self._init = False
        self._indexPath = self._config.logging.index_path
        self._logPath = self._config.logging.output_path + 'output/' + self._config.user_input.log_name + '-' + self._timestamp + '/video'


    def refresh(self):
        """
        Refresh the stream via bash using the updated parameters
        :return:
        """
        if (self._init):
            self.close()
        logger.info('re-initializing steam with new inputs')
        newCall = 'nohup' + ' node '+ self._indexPath + ' -w '  + self._resolution[0] + ' -h ' + self._resolution[1] + ' -b ' \
                  + str(self._bitrate) + ' -f ' + self._logPath + ' >/dev/null 2>&1 &'
        logger.info(newCall)

        subprocess.call([newCall], shell=True)


    def issue(self, myCode):
        """
        Update the bitrate and resolution given the code from terminal and then refresh the stream
        :param myCode:
        :return:
        """
        rawBit = raw_input("What bitrate? (1-9)")
        if RepresentsInt(rawBit) and rawBit > 1 and rawBit < 10:
            self._bitrate = int(rawBit) * 1000 #converting Mb/s to Kb/s

        #update res 640x480
        if myCode == 'low res stream':

            logger.info('re-initializing steam with new inputs')
            self._resolution = ['640', '480']

        #update res 1280x960
        elif myCode == 'high res stream':

            logger.info('re-initializing steam with new inputs')
            self._resolution = ['1280', '960']

        #Refresh stream
        self.refresh()
        self._lastCommand = myCode


    def open(self):
        """
        Open stream with default parameters
        :return:
        """
        self._resolution = ['640', '480']
        self._bitrate = 4000
        self.refresh()
        self._init = True

    def close(self):
        """
        Close the stream
        :return:
        """
        if (self._init):
            logger.info('closing stream')
            subprocess.call(["node " + self._indexPath + " --close"], shell=True)
            self._init = False
        else:
            print("Stream not running")
            logger.info("Stream not running")

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
try:
        int(s)
        return True
    except ValueError:
        return False

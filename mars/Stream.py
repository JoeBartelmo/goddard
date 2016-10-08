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

    def __init__(self, config, timestamp, clientIp = None):
        self._config = config
        self._timestamp = timestamp
        self._init = False
        self._indexPath = self._config.maven.path
        self._logPath = self._config.logging.output_path + 'output/' + self._config.user_input.log_name + '-' + self._timestamp + '/video'
        if clientIp is None:
            self._clientIp = '127.0.0.1';
        else:
            self._clientIp = clientIp

    def refresh(self):
        """
        Refresh the stream via bash using the updated parameters
        :return:
        """
        if (self._init):
            self.close()
        logger.info('re-initializing steam with new inputs')
        newCall = 'nohup' + ' node '+ self._indexPath + ' -i ' + self._clientIp + ' -f ' + self._logPath + ' >/dev/null 2>&1 &'
        logger.info('Launching Maven with: ' + newCall)

        subprocess.call([newCall], shell=True)

    def open(self):
        """
        Open stream with default parameters
        :return:
        """
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


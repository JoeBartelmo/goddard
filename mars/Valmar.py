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

import json
import subprocess
import logging
import os

logger = logging.getLogger('mars_logging')

class Valmar(object):
    '''
    Handles communication between the C++ Valmar program
    and Mars
    '''

    def __init__(self, config, bufferSize = 8096):
        self._config = config
        self._path = self._config.valmar.path
        self._commandPath = self._config.valmar.command_path
        self._beamGapPipe = self._config.valmar.beam_gap_path
        self._validCommands = {"enabled": {
                                    "type": "boolean",
                                    "parent": "command"
                                },
                                "refresh_frame_interval": {
                                    "type": "int",
                                    "parent": "command"
                                },
                                "gain": {
                                    "type": "int",
                                    "parent": "capture"
                                },
                                "sharpness": {
                                    "type":"float",
                                    "parent": "capture"
                                },
                                "threshold": {
                                    "type":"int",
                                    "parent": "processing"
                                }
        }
        self._init = False
        self._bufferSize = bufferSize
        self._io = os.open(self._beamGapPipe, os.O_RDONLY | os.O_NONBLOCK)

    def refresh(self):
        if self._init == True:
            self.disable()
        else:
            newCall = 'nohup ' + self._path + ' ' + self._commandPath + ' > /dev/null &'
            logger.info('Launching Valmar with: ' + newCall)
            subprocess.call([newCall], shell=True)

    def issueCommand(self, parameter, value):
        '''
        Our Commands enable them to change settings in the JSON file
        Valmar reads from this JSON every 100 frames
        '''
        if parameter in self._validCommands:
            typeOf = self._validCommands[parameter]["type"]
            try:
                if 'int' in typeOf:
                    var = int(value)
                elif 'float' in typeOf:
                    var = float(value)
                elif 'boolean' in typeOf:
                    var = bool(value)
                else:
                    raise ValueError
            except ValueError:
                logger.warning('Supplied value for ' + parameter + ' was not valid type');
                return
            with open(self._commandPath, 'r+') as commandFile:
                commands = json.load(commandFile)
                commands[self._validCommands[parameter]["parent"]][parameter] = value
                commandFile.seek(0, 0)
                commandFile.write(json.dumps(commands, indent=2, separators=(',', ': ')))
                commandFile.truncate()
        else:
            logger.warning('Valmar setting "' + parameter + '" does not exist')

    def getBeamGapData(self):
        '''
        Opens the FIFO and reads from it if possible
        '''
        """
        try:
            buffer = os.read(self._io, self._bufferSize)
        except OSError as err:
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                buffer = None
            else:
                raise
        if buffer is None:
            return None
        elif len(buffer) > 0:
            #data is piped through as json
            beamGapData = json.load(buffer)
        """
        pass


    def enable(self):
        self.issueCommand("enabled", True)
        self.refresh()
        self._init = True

    def disable(self):
        self.issueCommand("enabled", False)
        self._init = False

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
import errno
import os
import struct

logger = logging.getLogger('mars_logging')

class Valmar(object):
    '''
    Handles communication between the C++ Valmar program
    and Mars
    '''

    def __init__(self, config):
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
        self._bufferSize = 4#always start by reading an integer

    def refresh(self):
        if self._init == True:
            self.disable()
        else:
            #delete fifo
            if os.path.exists(self._beamGapPipe):
                os.unlink(self._beamGapPipe)
            os.mkfifo(self._beamGapPipe)
            while not os.path.exists(self._beamGapPipe):
                time.sleep(1)
            newCall = self._path + ' ' + self._commandPath + ' &'
            logger.info('Launching Valmar with: ' + newCall)
            subprocess.call([newCall], shell=True)
            self._io = os.open(self._beamGapPipe, os.O_RDONLY | os.O_NONBLOCK)
    
    def swap32(self, x):
        return (((x << 24) & 0xFF000000) |
                ((x <<  8) & 0x00FF0000) |
                ((x >>  8) & 0x0000FF00) |
                ((x >> 24) & 0x000000FF))
    
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
        try:
            #first bit of data is an integer, which we convert to python land
            dist_length = os.read(self._io, self._bufferSize)
        except OSError as err:
            if err.errno == errno.EAGAIN or err.errno == errno.EWOULDBLOCK:
                dist_length = None
            else:
                raise
        if dist_length is None:
            return None
        elif len(dist_length) == 4:
            #data is piped through as an array, we need to parse to list.
            buff = None
            dist_length = struct.unpack('i', dist_length)[0]
            logger.debug("Receiving Data from valmar...")
            if dist_length == 0:
                return None
            while buff is None or len(buff) < 0:
                try:
                    #first bit of data is an integer, which we convert to python land
                    buff = os.read(self._io, dist_length)
                except OSError as err:
                    if err.errno != errno.EAGAIN and err.errno != errno.EWOULDBLOCK:
                        raise
            logger.debug(buff)
            return json.loads(buff)
    
    def enable(self):
        self.issueCommand("enabled", True)
        self.refresh()
        self._init = True

    def disable(self):
        self.issueCommand("enabled", False)
        self._init = False

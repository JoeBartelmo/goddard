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
import re

class Valmar():

    def __init__(self, config, mars):
        self._config = config
        self._commandPath = self._config.valmar.command_path
        self._telemetryPath = self._config.valmar.telemetry_path

        self._commands = {}
        self._telemetry = {}
        self._mars = mars


    def issueCommand(self, parameter, value):
        with open(self._commandPath),'r' as commandFile:
            self._commands = json.load(commandFile)
            self._commands[parameter] = value

        with open(self._commandPath, 'w') as commandFile:
            commandFile.write(json.dumps(self._commands))


    def updateTelemetry(self):
        with open(self._telemetryPath, 'r') as telemFile:
            self._telemetry = json.load(telemFile)
        return self._telemetry

    def enable(self):
        self.issueCommand("enable", True)

    def disable(self):
        self.issueCommand("enable",False)


import json

class Valmar():


    def __init__(self, jetson):
        self._jetson = jetson
        self._commandPath = self._jetson._config.valmar.commandPath
        self._telemetryPath = self._jetson._config.valmar.telemetryPath
        self._beamGapPath = self._jetson._config.valmar.beamGapPath

        self._commands = {}
        self._telemetry = {}
        self._beamGap = ""


    def modifyCommandParameter(self, parameter, value):
        with open(self._commandPath),'r' as commandFile:
            self._commands = json.load(commandFile)

            self._commands[parameter] = value

        with open(self._commandPath, 'w') as commandFile:
            commandFile.write(json.dumps(self._commands))


    def updateAll(self):
        self.updateTelemetry()
        self.updateBeamGap()


    def updateTelemetry(self):
        with open(self._telemetryPath, 'r') as telemetryFile:
            self._telemetry = telemetryFile.readlines()[-1]

        return self._telemetry


    def updateBeamGap(self):
        with open(self._beamGapPath) as beamFile:
            self._beamGap = beamFile.read(beamFile)

        return self._beamGap




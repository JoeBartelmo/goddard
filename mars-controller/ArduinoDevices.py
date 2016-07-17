import logging


class LED(object):

    def __init__(self):
        self._LEDcodes = ['brightness']
        self._lastCommand = None
        self._brightness = 0



    def issue(self, arduino):
        self._arduino = arduino

        rawBright = raw_input("How bright? (0-9)")
        if RepresentsInt(rawBright):
            self._brightness = rawBright
        else:
            logging.info("Brightness must be 0-9")

    def write(self):
        self._arduino.write('L' + str(self._brightness))


class Motor(object):

    def __init__(self):
        self._motorCodes = ['forward', 'backward', 'enable brake', 'disable brake', 'enable motor', 'disable motor']
        self._speed = 0
        self._lastCommand = None
        self._direction = 0
        self._brake = 0
        self._enabled = 0

    def issue(self, myCode, arduino):
        self._arduino = arduino

        if myCode in ('forward', 'backward'):
            self.movement(myCode)
        elif myCode in ('enable motor', 'disable motor'):
            self.toggleMotor(myCode)
        elif myCode in ('enable brake', 'disable brake'):
            self.toggleBrake(myCode)


    def movement(self, myCode):

        rawSpeed = raw_input("How fast? (0-9)")
        if RepresentsInt(rawSpeed):
            if int(rawSpeed) < 10 and int(rawSpeed) >= 0:
                self._speed = rawSpeed
                if myCode == 'forward':
                    self._direction = 1
                else:
                    self._direction = 0

        else:
            logging.info("Speed must be 0-9. Direction must be forward or backward.")

        if self._enabled == 0:
            logging.info("Motor must be enabled before you can move! Use: enable motor")
        if self._brake == 1:
            logging.info("Brake must be disabled to move! Use: disable break")

        self.write()


    def toggleMotor(self, myCode):
        if myCode == 'enable motor':
            self._enabled = 1
        elif myCode == 'disable motor':
            self._enabled = 0

        self.write()

    def toggleBrake(self, myCode):
        if myCode == 'enable brake':
            self._brake = 1
        elif myCode == 'disable brake':
            self._brake = 0

        self.write()

    def start(self):
        self._speed = 4
        self._direction = 1
        self._enabled = 1
        self._brake = 0

        self.write()

    def brake(self):
        self._arduino.write("M0010")
        logging.info("Arduino braking...")


    def write(self):
        print('M' + str(self._enabled) + str(self._direction) + str(self._brake) + str(self._speed))
        self._arduino.write('M' + str(self._enabled) + str(self._direction) + str(self._brake) + str(self._speed))




def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
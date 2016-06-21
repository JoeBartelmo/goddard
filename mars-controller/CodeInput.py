'''
ark9719
6/17/2016
'''
import logging
import subprocess

class ConcreteMotorInput(object):
    """
    ConcreteMotorInput is a concrete implementation of the CodeInput base class used to check validity
    on Motor control input strings.

    FORMAT ==> MABCD
    'M' is the motion identifer "M"
    'A' is a binary operator to enable the Motor (motor must be enabled to move at all)
    'B' is a binary operator that defines direction (fwd, rev)
    'C' is a binary operator to engage the brake
    'D' is a decimal integer (0-9) that defines the speed(Each integer roughly corresponds 1Mph or .5m/s)
    """
    def __init__(self, code):
        self._code = code
        self._type = 'M'

    def valid(self):

        #Check for binary inputs at positions A, B, C
        for c in self._code[1:4]:
            if int(c) not in (0, 1):
                logging.warning("Bad motor input entered")
                print("The second, third, or fourth integer in your code is not binary (0-1)")
                return False

        #Check for correct length
        if (len(self._code) != 5):
            logging.warning("Bad motor input entered")
            print("Incorrect code length, 1 character and 4 digits please.")
            return False

        #Check if D is integer
        if(not RepresentsInt(self._code[4])):
            logging.warning("Bad motor input entered")
            print("The last character in the code must be an integer.")
            return False

        return True

    def issue(self, arduino):
        arduino.write(self._code)
        logging.info("Control code written to Arduino.")





class ConcreteLEDInput():
    """
    ConcreteLEDInput is a concrete implementation of the CodeInput Base class used to check validity
    on LED control input strings.

    FORMAT ==> 'LX'
    L identifies LED, X is an integer (0-9) defining brightness
    """
    def __init__(self, code):
        self._code = code
        self._type = 'L'

    def valid(self):

        #Check for code length and the second character to be int
        if (len(self._code) == 2 and RepresentsInt(self._code[1]) ):
            return True
        else:
            logging.warning("Bad LED input entered")
            print("Code was not length two or the second character was not an integer")
            return False

    def issue(self, arduino):
        arduino.write(self._code)
        logging.info("Control code written to Arduino.")

class ConcreteStreamInput():
    """
    ConcreteStreamInput is a class for codes intended to dynamically change stream settings

     FORMAT ==> SAB
    'S' is the stream code identifier
    'A' is the resolution changer [ 0 (640x480) or 1 (1280 x 960)]
    'B' is the bitrate integer (0-9)
    """

    def __init__(self, code):
        self._code = code
        self._type = 'S'

    def valid(self):

        #Check code length
        if(len(self._code) != 3 ):
            logging.warning("Bad stream input entered")
            print("Code must be 3 characters long.")
            return False

        #Check first character for 0, 1
        if not RepresentsInt(self._code[1]) and not (self._code[1] in (0, 1, 2)):
            logging.warning("Bad stream input entered")
            print("Second character must be  0, 1, or 2.")
            return False

        #Check if 3rd character is int
        if not RepresentsInt(self._code[2]):
            logging.warning("Bad stream input entered")
            print("Third character must be integer (0-9).")
            return False

        return True

    def issue(self, arduino):

        bitrate = self._code[2]

        #640x480
        if int(self._code[1]) == 0:
            #TODO
            subprocess.call("Placeholder for stream code syntax ")
        #1280x960
        elif int(self._code[1]) == 2:
            #TODO
            subprocess.call("Placeholder for stream code syntax ")







def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

"""
def testing():
    mCodes = ['M0001', 'M0102', 'M000234', 'M000Q']
    lCodes = ['L1', 'LA', 'L123']
    sCodes = ['S123', 'SAB', 'S12345', 'S1A', 'SA1' ]

    for code in sCodes:
        testCode = ConcreteStreamInput(code)

        print(code + ' evaluates to : ')
        print(testCode.valid())
        print("-----------")



testing()
"""
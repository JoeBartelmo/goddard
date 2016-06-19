'''
ark9719
6/17/2016
'''

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

    def valid(self, code):

        for c in code[1:4]:
            binaryBool = (c == 0 or c == 1)
            if binaryBool == False:
                print("The second, third, or fourth integer in your code is not binary (0-1)")
                return False

        if (len(code) != 5):
            print("Incorrect code length, 1 character and 4 digits please.")
            return False

        if(code[4].isdigit() == False):
            print("The last character in the code must be an integer.")

        return True




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

    def valid(self, code):
        if (len(code) == 2 and code[1].isdigit() ):
            return True
        else:
            return False





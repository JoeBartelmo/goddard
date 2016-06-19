'''
ark9719
6/17/2016
'''
from Arduino import Arduino
from Jetson import Jetson
from Mars import Mars
from Threads import InputThread
from Threads import StatisticsThread
import logging
import sys
import json
from collections import namedtuple

#Assumes that the server handeled validation
def parseConfig(json_string):
    config = json.loads(json_string, object_hook=lambda configObject: namedtuple('X', configObject.keys())(*configObject.values()));
    return config

def run(json_string):
    print("Starting...")
    logging.basicConfig(filename='log.txt', level=logging.INFO)
    logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    print("Loading configurations...")
    #Populate config
    logging.info('Reading in settings configurations')
    config = parseConfig(json_string)

    print("Connecting arduino...")
    #Connect Arduino
    logging.info('Attempting to connect Arduino')
    myArduino = Arduino(config)

    #Flush buffers
    myArduino.flushBuffers()

    print("Starting Mars...")
    #Initilize Mars
    myMars = Mars(myArduino, config)

    print("Starting output...")
    #Initilize Jetson
    myJetson = Jetson(myArduino, config, myMars)

    #start threads
    startThreads(myJetson)


def startThreads(jetson):
        """
        This method starts the two threads that will run for the duration of the program. One scanning for input,
        the other generating, displaying, and saving data.
        :return:
        """
        logging.info("Attempting to start threads")

        try:
            inputT = InputThread(jetson)
            statsT = StatisticsThread(jetson)
            inputT.start()
            statsT.start()

        except Exception as e:
            logging.info("error starting Multithreading ({})".format(e))
            logging.info("program will terminate")
            sys.exit()

def main():
    if len(sys.argv) < 2:
        print('To few arguments, please specify a json string with which to load configuration')
        print('\tUsage: run.py json_string')
        return;
    print ('\ntest\n\n')
    print(sys.argv);
    sys.argv.pop(0);
    json_string = ''.join(sys.argv)
    print('\n\n\n' + json_string)
    run(json_string)

main()


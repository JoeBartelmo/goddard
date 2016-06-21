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
import time
import os.path
import json
from collections import namedtuple

#Assumes that the server handeled validation
def parseConfig(json_string):
    config = json.loads(json_string, object_hook=lambda configObject: namedtuple('X', configObject.keys())(*configObject.values()));
    return config

def initOutput(config):
    t = time.localtime()
    timestamp = time.strftime('%b-%d-%Y_%H%M', t)

    if not os.path.exists('output/' + timestamp + '/'):
        os.makedirs('output/' + timestamp + '/')

    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join('output/' + timestamp + '/', "log.txt"),"w")
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if (os.path.isfile('output/' + timestamp + '/' + config.logging.logName + '_machine_log.csv')):
        print("The output file you specified in the configuration file already exists.\n")
        print("The statistics from the previous reads will be overwritten if you don't specify a new file.")
        print("Do you wish to continue?")
        answer = raw_input("Y / N: ")
        if answer.lower() in ('n', 'no'):
            print ("The program will terminate ")
            sys.exit()

    return timestamp


def run(json_string):
    print("Starting...")

    print("Loading configurations...")
    #Populate config
    logging.info('Reading in settings configurations')
    config = parseConfig(json_string)

    logging.info("Preparing output directories")
    timestamp = initOutput(config)

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
    myJetson = Jetson(myArduino, config, myMars, timestamp)

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


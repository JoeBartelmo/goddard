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

import socket
import sys
import time
from fileListener import FileListenerThread
from listener import ListenerThread
import logging
from Queue import Queue
sys.path.insert(0, '../gui')
from gui import GUI
sys.path.insert(1, '../shared')
from ColorLogger import initializeLogger 
from sender import SenderThread
from threadManager import ThreadManager
from constants import *
import errno
from socket import error as socket_error
import threading

#defines whether or not we have closed threads already
closedThreads = False
def closeAllThreads():
    '''
    Cleans up all open sockets and threads on client
    '''
    global closedThreads
    if closedThreads == False:
        if manager is not None and manager.is_alive():
            manager.stop()
            manager.join()
        commandSocket.close()
    sys.exit()

def displayUsage(unknownObj = None):
    '''
    Prints userfriendly usage of client.py
    '''
    if unknownObj is not None:
        print('Unknown parameter, ' + str(unknownObj) + '\n')
    print('Incorrect arguments, please specify a json string or object with which to load configuration')
    print('\tUsage:\tclient.py [Server IP|Server Domain]')
    print('\t\t-d: Debug mode')
    print('\t\t-c: CLI (No GUI) mode')

if __name__ == '__main__':
    filename = sys.argv.pop(0)#client.py
    
    logMode = logging.INFO 
    cliMode = False    
    serverAddr = None

    #TODO: Install CLI and use that instead
    if len(sys.argv) < 1 or len(sys.argv) > 3:
        displayUsage()
        sys.exit(1)
    else:
        serverAddr = sys.argv.pop(0)
        while(len(sys.argv)):
            mode = sys.argv.pop(0)
            if mode == '-d':
                logMode = logging.DEBUG
            elif mode == '-c':
                cliMode = True
            else:
                displayUsage(mode)
                sys.exit(1)
    sys.argv.append(filename)#tkinter wants the filename to be there

    #grabbing server address from arguments
    logger = initializeLogger('./', logMode, 'mars_logging', sout = True, colors = True)
    logger.info('Using server address:' + serverAddr)

    #Queues responsible for communicating between GUI and this socket client
    guiTelemetryInput = Queue()
    guiDebugTelemetryInput = Queue()
    guiLoggingInput = Queue()
    guiOutput = Queue()
    guiBeamGapInput = Queue()
    destroyGUI = threading.Event()

    #thread responsibel for handling telemetry from mars
    telemThread = ListenerThread([guiTelemetryInput, guiDebugTelemetryInput], serverAddr, TELEMETRY_PORT, logMode, 'Telemetry Receive', displayInConsole = False)
    #thread responsible for handling mars logging
    debugThread = ListenerThread(guiLoggingInput, serverAddr, DEBUG_PORT, logMode, 'Logging Receive')
    #thread responsible for handling files sent from mars
    fileListenerThread = FileListenerThread(serverAddr, FILE_PORT)
    try:
        #socket that will send data to the server
        commandSocket = socket.create_connection((serverAddr, MARS_PORT))
    except socket_error as serr:
        if serr.errno != errno.ECONNREFUSED and serr.errno != -2:
            raise serr
        logger.critical('Was Unable to connect to ' + serverAddr + ':' + str(MARS_PORT))
        sys.exit()
    #socket that will maintain ping to server and send commands to server
    senderThread = SenderThread(serverAddr, PING_PORT, guiOutput, commandSocket)
    senderThread.start()#we need to start this up to establish communication

    threads = [senderThread, telemThread, debugThread, fileListenerThread]
    if cliMode:
        manager = ThreadManager(threads)
    else:
        myGUI = GUI(guiOutput, guiLoggingInput, guiTelemetryInput, guiDebugTelemetryInput, guiBeamGapInput, destroyGUI, serverAddr)
        manager = ThreadManager(threads, myGUI)
    try:    
        # Send configuration data
        with open('config.json', 'r') as content_file:
            message = content_file.read().replace('\n','').replace(' ', '')
        commandSocket.sendall(message)

        if manager.startThreadsSync() == True:
            manager.start()
            manager.startInterface(guiOutput, cliMode)
        else:
            logger.critical('Could not establish connection with mars, aborting.\n\tPossible Problems: Bad config.json, outdated client')
    except KeyboardInterrupt:
        closeAllThreads()
    finally:
        closeAllThreads()
else:
    displayUsage()


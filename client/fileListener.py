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

import threading
import struct
import pickle
import logging
from threading import Thread
import socket
import logging
from ColorLogger import initializeLogger 
from select import select
import struct
import errno
from socket import error as socket_error

logger = logging.getLogger('mars_logging') 

class FileListenerThread(threading.Thread):
    def __init__(self, serverAddr, port):
        super(FileListenerThread, self).__init__()
        self._stop = threading.Event()
        self.serverAddr = serverAddr
        self.port = port
        self.socketTimeout = 3
    
    def run(self):
        logger.debug('Client side FileListener Thread waiting for connectionn...')
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if self.serverAddr != 'localhost':
            listener.bind(('', self.port))
        else:
            listener.bind(('localhost', self.port))
        listener.listen(1)

        listenerConnection, address = listener.accept()
        listenerConnection.setblocking(0)
        listenerConnection.settimeout(self.socketTimeout)

        logger.warning('Client side "File Listener" Thread connected!')
        
        while self.stopped() == False:
            isReady = select([listenerConnection],[],[],self.socketTimeout)
            if isReady[0]:
                try:
                    fileNameLength = self.readIntFromSocket(listenerConnection)
                    if fileNameLength == -1:
                        break
                    fileName = listenerConnection.recv(fileNameLength)

                    logger.info('Downloading file [' + fileName + ']')

                    fileLength = self.readIntFromSocket(listenerConnection)
                    fileBase64Str = ''
                    while len(fileBase64Str) < fileLength:
                        bytesToRead = 64
                        if fileLength - len(fileBase64Str) < bytesToRead:
                            bytesToRead = fileLength - len(fileBase64Str)
                        fileBase64Str += listenerConnection.recv(bytesToRead)

                    with open(fileName, 'wb') as f:
                        f.write(fileBase64Str.decode('base64'))
                except socket_error as serr:
                    if serr.errno == errno.ECONNREFUSED or serr.errno == errno.EPIPE:
                        logger.critical('Was not able to connect to File Listener socket, closing app')
                        break
                    raise serr
                    
        logger.warning('Closing listener socket')
        listenerConnection.shutdown(2)
        listener.shutdown(2)
        listenerConnection.close()
        listener.close()
        logger.warning('Client Side "File Listener" Thread Stopped')
        
        self.stop()
    
    def readIntFromSocket(self, listenerConnection):
        data = listenerConnection.recv(4)
        if data is None or len(data) == 0:
            return -1
        return int(struct.unpack('I', data)[0])
    
    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()


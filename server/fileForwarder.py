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
import time
import os
import socket
import logging
import struct
import base64

logger = logging.getLogger('mars_logging')
directoryToScan = '../mars/files/'

class FileRelay(threading.Thread):
    def __init__(self, serverAddr, port):
        super(FileRelay, self).__init__()
        self._stop = threading.Event()
        self._socket = socket.create_connection((serverAddr, port))

    def run(self):
        while self.stopped() is False:
            filesToSend = os.listdir(directoryToScan)
            filesToSend.remove('.gitignore')#we need gitignore to commit this folder >.>
            if len(filesToSend) > 0:
                for filename in filesToSend:
                    with open(directoryToScan + filename, 'rb') as f:
                        fileInBytes = f.read()
                    logger.info('Sending file ' + filename + ' to the client')
                    
                    intPacker = struct.Struct('I')
                    
                    value = (len(filename),)
                    self._socket.sendall(intPacker.pack(*value))
                    self._socket.sendall(filename)
                    
                    base64File = base64.b64encode(fileInBytes)
                    value = (len(base64File), )
                    self._socket.sendall(intPacker.pack(*value))
                    self._socket.sendall(base64File)

                    os.remove(directoryToScan + filename)

            time.sleep(3)
        self._socket.shutdown(2)
        self._socket.close()
        logger.info('File Relay Thread stopped')

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()


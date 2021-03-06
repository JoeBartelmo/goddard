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

import sys
import socket
from validate import validate_json
from Queue import Queue
from Queue import Empty
from socketManager import SocketManager
from listener import ListenerThread
from marsHandler import MarsThread

#Manipulatable Variables
MARS_PORT = 1337
PING_PORT = 1341

#socket to receive commands from client
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('', MARS_PORT)
sock.bind(server_address)
sock.listen(1)

#Socket to maintain ping from client
pingSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ping_address = ('', PING_PORT)
pingSocket.bind(ping_address)
pingSocket.listen(1)

#this is the queue used for the client to communicate to the server,
#which pipes data to mars
commandQueue = Queue()
#this is the queue that notifies mars that the client is connected
connectionQueue = Queue()
#this is the queue that mars uses to notify the server that it's online
onlineQueue = Queue()

#defines mars handler thread, responsible for keeping mars alive
handler = None
#defines the listener thread, responsible for keeping communication alive between
#server and client
listener = None
#defines the socket thread, responsbile for handling mars' transmission from the server to the client
client = None
#defines whether or not we have closed threads already
closedThreads = False

def startMars(configuration, ipAddress): 
    print 'Mars as found to not be online, starting...'
    global handler
    handler = MarsThread(configuration, commandQueue, connectionQueue, onlineQueue, ipAddress, True)
    handler.start()

def closeAllThreads():
    global closedThreads
    if closedThreads == False:
        print 'Closing listener...'
        if listener is not None:
            listener.stop()
            listener.join()
        print 'Closing handler...'
        if handler is not None:
            handler.stop()
            handler.join()
        print 'Closing client...'
        if client is not None:
            client.joinZombie()
            client.join()
        print 'Closing sockets...'
        sock.close()
        pingSocket.close()
        closedThreads = True

try:
    while True:
        print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
        print 'At any time you can ^C to safely disconnect the server and stop mars'
        connection, client_address = sock.accept()
        pingConnection, ping_address = pingSocket.accept()

        client_ip, client_port = client_address
        print >>sys.stderr, 'connection from', client_ip
        
        #no matter what The client will always send a json config data
        data = connection.recv(4096)
        print >>sys.stderr, 'received "%s"' % data
        
        if data is not None:
            if listener is None or listener.stopped():
                if validate_json(data):
                    listener = ListenerThread(commandQueue, connectionQueue, connection, pingConnection)
                    listener.start()
                    client = SocketManager(commandQueue, connectionQueue, onlineQueue, client_ip, connection, listener) 
                    client.start()
                    try:
                        online = onlineQueue.get(timeout=2)
                        if online == 0:
                            startMars(data, client_ip)
                    except Empty:
                        startMars(data, client_ip)
            else:
                print 'There is already a client connected, booting new client'
except KeyboardInterrupt:
    closeAllThreads()
finally:
    closeAllThreads()

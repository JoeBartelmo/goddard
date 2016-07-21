import socket
import sys
import time
import struct
import pickle
import logging
from threading import Thread

marsPort = 1337
logPort = 1338

# Create TCP/IP sockets, order specified cannot be changed.
telemetry = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
telemetry.bind(('localhost', logPort))
telemetry.listen(1)
sock = socket.create_connection(('localhost', 1337))


telemetryConnection, server_address = telemetry.accept()
print 'Mars Socket and TelementryLog Socket Established!!!'


#https://docs.python.org/2/howto/logging-cookbook.html
#https://docs.python.org/2/library/logging.html#logging.LogRecord
def receieveTelemetry(connection):
    while True:
        chunk = connection.recv(4)
        if len(chunk) < 4:
            break
        slen = struct.unpack('>L', chunk)[0]
        chunk = connection.recv(slen)
        while len(chunk) < slen:
            chunk = chunk + connection.recv(slen - len(chunk))
        obj = pickle.loads(chunk)
        record = logging.makeLogRecord(obj)
        print record.msg


try:    
    # Send data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)
    thread = Thread(target = receieveTelemetry, args = (telemetryConnection, ))
    thread.start()
    while True:
        command = raw_input()
        sock.sendall(command)
    
except KeyboardInterrupt:
    print 'closing socket'
    sock.close()
finally:
    print 'closing socket'
    sock.close()

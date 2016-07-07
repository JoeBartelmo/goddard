import socket
import sys
import time
import struct
import pickle
import logging

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
try:    
    # Send data
    with open('config.json', 'r') as content_file:
        message = content_file.read().replace('\n','').replace(' ', '')
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)
    while True:
            chunk = telemetryConnection.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = telemetryConnection.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + telemetryConnection.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            print record.msg
    #iwhile True:
    #    data = sock.recv(16)
    #    amount_received += len(data)
    #    if len(data) > 0:
    #       print >>sys.stderr, 'received "%s"' % data
except KeyboardInterrupt:
    print 'closing socket'
    sock.close()
finally:
    print 'closing socket'
    sock.close()

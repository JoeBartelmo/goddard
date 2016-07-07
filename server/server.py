import sys
sys.path.insert(0, '../mars-controller')
import socket
from validate import validate_json
import logging, logging.handlers
import run as Mars #note as long as __main__ is defined this will write a usage violation to the console

#Manipulatable Variables
marsPort = 1337
logPort = 1338

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ('localhost', marsPort)
sock.bind(server_address)
sock.listen(1)


rootLogger = logging.getLogger()
rootLogger.setLevel(logging.INFO)

while True:
    print >>sys.stderr, 'Server launched on socket 1337; waiting for client...'
    connection, client_address = sock.accept()
    try:
        print >>sys.stderr, 'connection from', client_address
        socketHandler = logging.handlers.SocketHandler('127.0.0.1', logPort)
        rootLogger.addHandler(socketHandler)
        logging.info('Connection Established.')
        while True:
            data = connection.recv(4096)
            #print >>sys.stderr, 'received "%s"' % data
            if data:
                if validate_json(data):
                    logging.info('Data verified as valid config, starting up Mars!')
                    Mars.run(data)
            else:
                logging.info('Mars Connection Ceased')
                break;
    except KeyboardInterrupt:
        connection.close()
    finally:
        connection.close()


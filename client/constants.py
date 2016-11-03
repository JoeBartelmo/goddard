import struct

#socket connection timeout or recv timeout
SOCKET_TIMEOUT = 5.5 
#rate to ping the sender
PING_RATE = .5
#structure to pack and send to the server (probably should be localized to sender.py
FLOAT_PACKER = struct.Struct('f')

#ports we use for communication between client and server
MARS_PORT      = 1337
DEBUG_PORT     = 1338
TELEMETRY_PORT = 1339
FILE_PORT      = 1340
PING_PORT      = 1341
#command to shutdown mars
MARS_KILL_COMMAND = 'exit'
#time in seconds to verify we weren't able to connect
TIME_TO_VERIFY_ESTABLISHED_CONNECTION = 4

import threading
import struct
import pickle
import logging
from threading import Thread

class ListenerThread(threading.Thread):
    def __init__(self, q, socket):
        super(ListenerThread, self).__init__()
        self._stop = threading.Event()
        self.q = q
        self.socket = socket

    def run(self):
        while self.stopped() is False:
            chunk = self.socket.recv(4)
            if len(chunk) < 4:
                break
            slen = struct.unpack('>L', chunk)[0]
            chunk = self.socket.recv(slen)
            while len(chunk) < slen:
                chunk = chunk + self.socket.recv(slen - len(chunk))
            obj = pickle.loads(chunk)
            record = logging.makeLogRecord(obj)
            if self.q is not None:
                self.q.put(record)
            print record.msg
        print 'Listener Thread Stopped'

    def stop(self):
        self._stop.set()
   
    def stopped(self):
        return self._stop.isSet()


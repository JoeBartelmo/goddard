import threading

class InputThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while 1:
            self._jetson.repeatInput()

    def stop(self):
        self._stop.set()

class StatisticsThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson
        self._stop = threading.Event()

    def run(self):
        while 1:
            self._jetson.statisticsController()

    def stop(self):
        self._stop.set()
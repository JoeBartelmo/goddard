import threading

class InputThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson

    def run(self):
        while 1:
            self._jetson.repeatInput()

class StatisticsThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson

    def run(self):
        while 1:
            self._jetson.statisticsController()
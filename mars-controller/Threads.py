import threading

class InputThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson
        self._is_running = False

    def run(self):
        while not self._is_running:
            self._jetson.repeatInput()

    def stop(self):
        self._is_running = True

class StatisticsThread(threading.Thread):
    def __init__(self, jetson):
        threading.Thread.__init__(self)
        self._jetson = jetson
        self._is_running = False

    def run(self):
        while not self._is_running:
            self._jetson.statisticsController()

    def stop(self):
        self._is_running = True
import Tkinter as Tk
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backend.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
from matplotib.figure import Figure
from Queue import Empty

from VisualConstants import MARS_PRIMARY
MARS_PRIMARY = MARS_PRIMARY()
#MARS_MOTOR = MARS_MOTOR()
#MARS_DISP = MARS_DISP()
#MARS_ELEC = MARS_ELEC()
#MARS_CAM = MARS_CAM()

class Monitor(object):
    def __init__(self, telemetrySrc, plotter=MARS_PRIMARY )
        self._telemetryQueue = telemetryQueue
        self._plotter = plotter
        self._updates = None


    def retrieve_values(self)
        """
        Updates telemetry values from src
        """
        try:
            if not self._telemetryQueue.empty():
                return self._telemetryQueue.get(False)
            return None
        except Empty:
            return None

    def update(self):
        updates = retrieve_values()
        if updates is not None:
            for key in self._plotter._subplotIDs:
                xKey,yKey = key.split(":")
                x = updates[xKey]
                y = updates[yKey]

                self._plotter.graph(key,x,y)


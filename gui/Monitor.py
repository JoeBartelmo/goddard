import Tkinter as Tk
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backend.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
from matplotib.figure import Figure


from MarsConstants import MARS_PRIMARY
MARS_PRIMARY = MARS_PRIMARY()
#MARS_MOTOR = MARS_MOTOR()
#MARS_DISP = MARS_DISP()
#MARS_ELEC = MARS_ELEC()
#MARS_CAM = MARS_CAM()

"""
1) RunClock,SystemVoltage
2) RunCLock,BatteryRemaining
3) RunClock,TotalDisplacement
4) IBeam,TotalDisplacement
5) SetSpeed,RPM
6) RPM,Speed
 
"""

class Monitor(object):
    def __init__(self, telemetrySrc, plotter=MARS_PRIMARY )
        self._telemetrySrc = telemetrySrc
        self._plotter = plotter
        self._updates = None


    def retrieve_values(self)
        """
        updates telemetry values from src
        """
        with open(self._telemetrySrc, 'r', as srcFile:
            self._updates = json.load(srcFile)
        return self._updates

    def update(self):
        updates = retrieve_values()

        for key in self._plotter._subplotIDs:
            xKey,yKey = key.split(":")
            x = updates[xKey]
            y = updates[yKey]

            self._plotter.graph(key,x,y)
         

    def display(self):
        window = Tk()
        myLabel = Label(window, text="MARS STATUS")
        myLabel.pack()

import Tkinter as Tk
import matplotlib.pyplot as plt
from matplotlib.backend.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

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
    def __init__(self, telemetrySrc, plotter=MARS_PRIMARY() )
        self._telemetrySrc
        self._plotter = plotter

    def update(self)
        retrieve_values()
        plot()

    def retrieve_values(self)
        """
        updates telemetry values from src
        """
        with open(self._telemetrySrc, 'r', as srcFile:
            self._values = json.load(srcFile)
        return self._values

    def plot(self):
        for plotNum in range(1,plotter._numPlots+1):
            ID1 = plotter._valueIDs[ plotNum[0] ]
            ID2 = plotter._valueIDs[ plotNum[1] ]
            value1 = self._values[ ID1 ]
            value2 = self._values[ ID2 ]
            self._plotter.draw(plotNum,value1,value2)

    def display(self):
        window = Tk()
        myLabel = Label(window, text="MARS STATUS")
        myLabel.pack()

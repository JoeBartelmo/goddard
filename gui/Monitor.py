import Tkinter as tk
import matplotlib
matplotlib.use("TkAgg")

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
from Queue import Empty

from VisualConstants import MARS_PRIMARY
MARS_PRIMARY = MARS_PRIMARY()
#MARS_MOTOR = MARS_MOTOR()
#MARS_DISP = MARS_DISP()
#MARS_ELEC = MARS_ELEC()
#MARS_CAM = MARS_CAM()

class Monitor(tk.Frame):
    def __init__(self, parent, plotter=MARS_PRIMARY):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent
        
        self._telemetry_data = {}
        self._plotter = plotter
        self._updated = False
        
        self.init_ui()
        self.update_loop()

    def init_ui(self):
        """ Initialize visual elements of widget. """
        #configure subPlot and canvas here
        self.canvas = FigureCanvasTkAgg(self._plotter._fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column = 0, rowspan = 2, sticky = 'nsew')
       
        #configure botttom label here 
        self.label = tk.Label(self, text='Std. Dev.: None\t\tBeam Number: 0',justify='left')
        self.label.grid(row=2, column=0, sticky='sew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid()
        self.update()
    
    def set_telemetry_data(self, telemetryData):
        '''
        Called on by Async thread
        '''
        self.telemetry_data = telemetryData
        self._updated = True

    def update_loop(self):
        if self._updated:
            self._update = False
            for key in self._plotter._subplotIDs:
                xKey,yKey = key.split(":")
                x = updates[xKey]
                y = updates[yKey]

                self._plotter.graph(key,x,y)
        self.after(100, self.update_loop)

if __name__=='__main__':
    root = tk.Tk()
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    monitor = Monitor(root)
    monitor.grid(column = 0, row = 0, sticky = 'nsew')
    root.mainloop()

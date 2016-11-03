import Tkinter as tk
import matplotlib

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
from Queue import Empty

from VisualConstants import MARS_PRIMARY

class Monitor(tk.Frame):
    def __init__(self, parent, plotter):
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
        self.canvas.get_tk_widget().grid(row=1, column = 0, sticky = 'nsew')
        #useful little toolbar that uses pack() so we have to put it in a seperate frame and bind to bottom
        frame = tk.Frame(self)
        frame.grid(row = 0, column = 0, sticky = 'ew')
        toolbar = NavigationToolbar2TkAgg(self.canvas, frame)
        toolbar.update()
        #configure botttom label here 
        self.label = tk.Label(self, text='Std. Dev.: None\t\tBeam Number: 0',justify='left')
        self.label.grid(row=2, column=0, sticky='sew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        #self.grid()
        self.update()
    
    def set_telemetry_data(self, telemetryData):
        '''
        Called on by Async thread
        '''
        self.telemetry_data = telemetryData
        self._updated = True

    #TODO: currently works but needs to be very optimized...
    #maybe update asynchronously, graphs are costly
    #or only plot when in frame, and halt cameras when out of frame
    def update_loop(self):
        '''if self._updated:
            self._update = False
            for key in self._plotter._subplotIDs:
                split = key.split(":")
                x = self.telemetry_data[split[0]]
                y = self.telemetry_data[split[1]]

                self._plotter.graph(key,x,y)
        self.after(100, self.update_loop)'''

if __name__=='__main__':
    root = tk.Tk()
    import ttk
    notebook = ttk.Notebook(root)
    notebook.grid(row = 0, column = 0, sticky = 'nsew')
    root.grid_columnconfigure(0, weight=1)
    root.grid_rowconfigure(0, weight=1)
    monitor = Monitor(root, MARS_PRIMARY(1))
    monitor.grid(column = 0, row = 0, sticky = 'nsew')
    fr = tk.Frame(root)
    fr.grid(row = 0, column = 0, sticky = 'nsew')
    
    initial_im = tk.PhotoImage(file = 'assets/rit_imaging_team.png')
    image_label = tk.Label(fr, image=initial_im)
    image_label.grid(row=0, column=0, rowspan = 2, sticky = 'nsew')
    notebook.add(monitor, text = 'testing')
    notebook.add(fr, text = 'testing other')
    root.mainloop()

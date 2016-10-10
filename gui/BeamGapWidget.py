# Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial 
# portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
# LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import matplotlib
matplotlib.use('TkAgg')
import numpy
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib.figure import Figure
import Tkinter as tk
from multiprocessing import Process
from Queue import Queue, Empty
import sys

from Threads import TelemetryThread


class BeamGapWidget(tk.Toplevel):
    '''
    Widget designed to display incoming beamgap data
    parent is the root container
    queue is a custom queue where each object contains only necessary
    information for this widget: Valmar data from telemetry json
    '''
    def __init__(self, parent, queue, **kwargs):
        tk.Toplevel.__init__(self, parent, **kwargs)
        self.queue = queue

        self.parent = parent
        self.protocol("WM_DELETE_WINDOW", self.onDelete)
        self._init_ui()
    
        self.updateloop()
    
    def onDelete(self):
        '''
        Destroy callback
        '''
        self.destroy()

    def _init_ui(self):
        # Image display label

        self.fig = Figure()
        self.gap = self.fig.add_subplot(111)
 
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column = 0, rowspan = 2, sticky = 'nsew')
        
        self.label = tk.Label(self, text='Std. Dev.: None\t\tBeam Number: 0',justify='left')
        self.label.grid(row=2, column=0, sticky='sew')

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
                   
    def beamGapDisplay(self, data):
        line = numpy.zeros(len(data)) + (data/2)
        lineLength = numpy.arange(0,len(data))
        std = numpy.std(data)
        stdL = line - std
        
        return line, lineLength, std, stdL

    def updateloop(self):
        try: 
            data = self.queue.get(False)
            ibeamNum = data['IbeamCounter']
            ibeamDist = numpy.asarray(data['BeamGap'])  
            print len(ibeamDist)
            
            #pipe that data to the beamGapDisplay function below
            line, lineLength, std, stdL = self.beamGapDisplay(ibeamDist)
            self.gap.cla()
            self.gap.plot(line, lineLength, 'r', \
                -line, lineLength, 'r', \
                stdL, lineLength, 'g--', \
                -stdL, lineLength, 'g--')
            #TODO: set to default beam gap width within some margin
            self.gap.set_xlabel('Distance (pix)')
            self.gap.set_ylabel('Beam Data Length (pix)')
            #self.gap.set_xlim() 
            self.gap.set_ylim(0,len(ibeamDist))
            self.label['text'] = 'Std. Dev:' + str(std) + '\t\tBeam Num:' + str(ibeamNum)
            
            self.canvas.draw()
        except Empty:
            pass
 
        self.after(100, self.updateloop)
        
if __name__ == '__main__':
    from Queue import Queue
    from MarsTestHarness import MarsTestHarness
    from threading import Thread

    telem_q = Queue()
    beam_q = Queue()
    mth = MarsTestHarness(telem_q, beam_q)

    Thread(target=mth.generateQueueData).start()
    Thread(target=mth.generateQueueData).run()

    #data = numpy.arange(0,1,0.05)
    root = tk.Tk()
    #t = BeamGapWidget(root, Queue())
    t = BeamGapWidget(root, beam_q)
    #t = BeamGapWidget(root, data)
    t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()
    sys.exit()


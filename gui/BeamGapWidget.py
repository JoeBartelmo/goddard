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


class BeamGapWidget(tk.Frame):
	
	def __init__(self, parent, client_queue_in):
		tk.Frame.__init__(self, parent, bd=2, relief='groove')
		self.queue = client_queue_in

		self.parent = parent
		
		self._init_ui()
		
		self.updateloop()
		
	def _init_ui(self):
		# Image display label

		self.fig = Figure()
		self.gap = self.fig.add_subplot(111)
		
		self.canvas = FigureCanvasTkAgg(self.fig, master=root)
		self.canvas.draw()
		self.canvas.get_tk_widget().pack(side='top', fill='both', expand=1)
		self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)
	        		
	def beamGapDisplay(self, data):
		line = numpy.zeros(len(data)) + (data/2)
		lineLength = numpy.arange(0,len(data))
		std = numpy.std(data)
		stdL = line - std
		
		return line, lineLength, std, stdL
	
	def updateloop(self):
		#TODO: Implement code to take in the self.queue
	        	
		#try: 
		#	data = self.queue.get(False)
                #except Empty:
		#	data = None

		#pipe that data to the beamGapDisplay function below
		line, lineLength, std, stdL = self.beamGapDisplay(data)

		self.gap.plot(line, lineLength, 'r', \
			-line, lineLength, 'r', \
			stdL, lineLength, 'g--', \
			-stdL, lineLength, 'g--')
		#TODO: set to default beam gap width within some margin
		self.gap.set_xlim(-1,1) 
		self.gap.set_ylim(0,len(data))
		self.gap.set_xlabel('Std. Dev: ' + str(std))
		self.gap.set_ylabel('Beam Number')
		self.canvas._tkcanvas.pack(side='top', fill='both', expand=1)
		self.canvas.draw()
		
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

	data = numpy.arange(0,1,0.05)
	root = tk.Tk()
	#t = BeamGapWidget(root, Queue())
	t = BeamGapWidget(root, beam_q)
	t = BeamGapWidget(root, data)
	t.grid()
	root.update()
	print t.winfo_height(), t.winfo_width()
	root.mainloop()
	sys.exit()
 

   
   

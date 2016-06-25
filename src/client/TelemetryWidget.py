import Tkinter as tk
from multiprocessing import Process, Queue
import sys

class TelemetryWidget(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        self.labels = []        
        self.label_text = ['RunClock: %s', 'Distance: %s', 'Speed: %s', \
        'Power: %s', 'Battery Remaining: %s', 'Integration Time: %s', \
        'Connected: %s', 'RPM: %s', 'System Voltage: %s', 'System Current: %s', \
        'Last Control Code: Motor: %s', 'L: %s', 'S: %s']
        
        self.telem_queue = Queue()

        for _text in self.label_text:
            self.labels.append(tk.Label(self, text=_text % ' '))

        for label in self.labels:   # put them all in a row
            label.grid(row=0,column=self.labels.index(label) + 1)
        
    def update(self, telemetry_list):
        for i in range(10):
            self.labels[i]['text'] = self.label_text[i] % telemetry_list[i]
        
    def persistent_update(self, delay=500):
        telem = self.telem_queue.get()
        # call update
        self.update(telem)
        self.frame.update()

        root.after(delay, self.persistent_update, delay)

    def get_data(self):
        while True:
            #get data from json or whereever
            #telem = TODO()
            if not telem: 
                continue
            self.telem_queue.put(telem)

if __name__=='__main__':
    root = tk.Tk()
    TelemetryWidget(root).grid()
    root.resizable(width=False, height=False)
    root.mainloop()
    sys.exit()

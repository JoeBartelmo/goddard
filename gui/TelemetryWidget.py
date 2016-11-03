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

import json
import Tkinter as tk
from Queue import Queue, Empty
import sys

from Threads import TelemetryThread

class TelemetryWidget(tk.Frame):
    """
    Shows structured output from valmar.

    Args:
        parent: parent window
    """
    def __init__(self, parent):
        tk.Frame.__init__(self, parent, bd=2, relief='groove')
        self.parent = parent

        #contains all pretty views
        self.translationKeys = self.load_keys('../gui/telemetryTranslation.json')
        self.labels = {}
        self.values = {}
        self.telemetry_data = {}

        #instantiate ui
        self.set_telemetry_ui()

        #start grabbing data
        self.update_telemetry_loop()

    def set_telemetry_ui(self, json_object = None):
        """ Initialize visual elements of widget. """
        index = 0
        for key, val in self.translationKeys.iteritems():
            # label
            if val['display']:
                if key not in self.labels:
                    #update label row
                    self.labels[key] = tk.Label(self, text=val['friendly_name'], padx=5, pady=5, bd=2, justify='left', relief='ridge', width=18)
                    self.labels[key].grid(row=val['display_order'], column=0, sticky='nsew')
                    #update value column
                    self.values[key] = tk.Label(self, padx=5, pady=5, width=18, anchor='w')
                    self.values[key].grid(row=val['display_order'],column=1, sticky='nsew')
                    self.telemetry_data[key] = ''
                    #make expandable
                    self.grid_rowconfigure(index, weight=1)
                    index += 1
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.parent.grid_columnconfigure(0, weight=1)
        self.parent.grid_rowconfigure(0, weight=1)
        self.grid()
        self.update()
       
    def set_telemetry_data(self, telemetryData):
        self.telemetry_data = telemetryData

    def update_telemetry_loop(self):
        for key, val in self.translationKeys.iteritems():
            if val['display']:
                #print 'Telemetry Data:'
                #print self.telemetry_data
                self.values[key]
                self.values[key]['text'] = self.telemetry_data[key]
        self.after(500, self.update_telemetry_loop)
    
    def load_keys(self, config_file):
        with open(config_file) as f:
            configuration = \
                json.load(f)#.replace('\n', '').replace(' ', '').replace('\r', '')
        return configuration

if __name__=='__main__':
    from Queue import Queue
    root = tk.Tk()
    t = TelemetryWidget(root, Queue())
    t.grid()
    root.update()
    print t.winfo_height(), t.winfo_width()
    root.mainloop()
    sys.exit()

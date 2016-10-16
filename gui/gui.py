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

import Tkinter as tk
import os
import tkMessageBox
from mainapp import MainApplication
from TopMenu import TopMenu
from BeamGapWidget import BeamGapWidget
from constants import *#remember you should run through client.py, not through gui.py, this will throw import error otherwise
import logging
from ttk import Notebook

logger = logging.getLogger('mars_logging')

class GUI(tk.Tk):
    """
    Start graphical interface for client.

    Args:
        client_queue_cmd: queue to send commands
        client_queue_log: queue to get logging info
        client_queue_telem: queue to get telemetry data
        beam_gap_queue: queue to retrieve beam gap data (any queue will do, this is handled via the gui, through the telemetry queue)
        @depricated
        server_ip: server IP address for rtp stream access
    """
    def __init__(self, client_queue_cmd, client_queue_log, client_queue_telem, client_queue_telem_debug, beam_gap_queue, destroyEvent, server_ip, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.client_queue_cmd = client_queue_cmd
        self.client_queue_log = client_queue_log
        self.client_queue_telem = client_queue_telem
        self.client_queue_telem_debug = client_queue_telem_debug
        self.beam_gap_queue = beam_gap_queue
        self.server_ip = server_ip
        self.destroyEvent = destroyEvent

    def init_ui(self):
        #make resizable
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.notebook = Notebook(self)
        self.notebook.grid(column = 0, row = 0, sticky = 'nsew')

        # define mainapp instance
        self.mainApplication = MainApplication(self.notebook, self.client_queue_cmd, self.client_queue_log, self.client_queue_telem, self.beam_gap_queue, self.destroyEvent, self.server_ip) 
        self.mainApplication.grid(column = 0, row = 0, sticky="nsew")
        self.notebook.add(self.mainApplication, text = "Main")
        # menu
        self.menu_ = TopMenu(self, '../gui/operations.json', self.client_queue_cmd, 'Commands')
        ### Add custom commands here
        self.menu_.add_menu_item('Reconnect to Cameras', self.mainApplication.start_streams, "View")
        self.menu_.add_menu_item('Left', self.mainApplication.focus_left, 'View/Camera Focus')
        self.menu_.add_menu_item('Center', self.mainApplication.focus_center, 'View/Camera Focus')
        self.menu_.add_menu_item('Right', self.mainApplication.focus_right, 'View/Camera Focus')
        self.menu_.add_menu_item('IBeam Display', self.beamGapGraph, 'View/Windows')
        ### 
        self.menu_.finalize_menu_items()
        self.config(menu=self.menu_)

        # title and icon
        self.wm_title('Hyperloop Imaging Team')
        img = tk.PhotoImage('../gui/assets/rit_imaging_team.png')
        self.tk.call('wm', 'iconphoto', self._w, img)
        
        #call destroyCallback on clicking X
        self.protocol('WM_DELETE_WINDOW', self.destroyCallback)
         
        self.geometry("900x500")
        self.update()

    def killMars(self):
        '''
        Sends the kill command to Mars
        '''
        self.client_queue_cmd.put('exit')

    def displayMarsDisconnected(self):
        tkMessageBox.showerror('Lost connection to Mars', 'The client has lossed connection to mars, closing application.')
        self.destroyClient()

    def destroyClient(self):
        self.menu_.destroy() 
        self.mainApplication.close_()
        self.notebook.destroy()
        self.destroy()

    def destroyCallback(self):
        '''
        Function called when the window handle Destory is clicked (the x)
        Opens up a small prompt asking if you wanna kill mars
        '''
        logger.debug('GUI entering destroy callback...')
        result = tkMessageBox.askyesno('Leaving GUI, Should Mars be Disabled?', 'Leaving GUI, should Mars be Disabled?')

        if result:
            self.killMars()
        self.destroyClient()

    def beamGapGraph(self):
        '''
        Function that launches the Beam Gap Widget that displays the current beam distances
        in readalbe form.
        '''
        if getattr(self, top, False) == False:
            self.top = BeamGapWidget(self, self.beam_gap_queue)
            self.top.title("VALMAR Beam Gap")
        else:
            if self.top['state'] != 'normal':
                self.top = BeamGapWidget(self, self.beam_gap_queue)
                self.top.title("VALMAR Beam Gap")

    def start(self):
        '''
        Starts the root window
        '''
        
        self.init_ui()
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.destroyClient()

if __name__=='__main__':
    print 'Please use goddard/client/client.py instead, this application requires client to function currently'
'''
The below is depricated and will need to be updated with a client test harness
    from Queue import Queue
    from ColorLogger import initializeLogger 

    logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)
    logger.debug('GUI is running independant of client, attempting to connect to server hyperlooptk1.student.rit.edu')

    cmd_queue = Queue()
    log_queue = Queue()
    telem_queue = Queue()
    beam_gap_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    start(cmd_queue, log_queue, telem_queue, beam_gap_queue, server_ip)

    while not cmd_queue.empty():
        print cmd_queue.get()    
'''


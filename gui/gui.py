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
import logging
from Monitor import Monitor
from ttk import Notebook
from Threads import TelemetryThread
import VisualConstants
#from PIL import ImageTk

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
    def __init__(self, client_queue_cmd, client_queue_log, client_queue_telem, beam_gap_queue, destroyEvent, server_ip, **kwargs):
        tk.Tk.__init__(self, **kwargs)
        self.client_queue_cmd = client_queue_cmd
        self.client_queue_log = client_queue_log
        self.client_queue_telem = client_queue_telem
        self.beam_gap_queue = beam_gap_queue
        self.server_ip = server_ip
        self.destroyEvent = destroyEvent

    def init_ui(self):
        #make resizable
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.notebook = Notebook(self)
        # define mainapp instance -- also manages above telemetry thread
        self.mainApplication = MainApplication(self, self.client_queue_cmd, self.client_queue_log, self.client_queue_telem, self.beam_gap_queue, self.destroyEvent, self.server_ip) 
        self.notebook.add(self.mainApplication, text = "Main")
        # define telemetry widgets
        self.monitor = Monitor(self, VisualConstants.MARS_PRIMARY(1))
        self.notebook.add(self.monitor, text = 'Monitor')
        self.notebook.grid(column = 0, row = 0, sticky = 'nsew')
        
        # menu -outside of notebook
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
        
        # start all operations here so we don't cause a hissyfit between tkinter and threads
        self.mainApplication.start_streams()
        #define telemetryThread
        self.tthread = TelemetryThread([self.mainApplication.telemetry_w, self.monitor], self.client_queue_telem, self.beam_gap_queue)
        self.tthread.start()

        # title and icon
        self.wm_title('Hyperloop Imaging Team')
        #this is garbage, i hate tkinter
        #self.img = ImageTk.PhotoImage(file='rit_imaging_team.xbm')
        #self.tk.call('wm', 'iconphoto', self._w, self.img)
        #self.iconbitmap('@rit_imaging_team.xbm')
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
        self.killTelemThread()
 
    def killTelemThread(self):
        """ Customized quit function to allow for safe closure of processes. """
        self.tthread.stop()
        if self.tthread.is_alive():
            self.tthread.join()

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
    '''
    from Queue import Queue
    import sys
    sys.path.insert(1, '../shared')
    from ColorLogger import initializeLogger 
    import threading

    logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)

    cmd_queue = Queue()
    log_queue = Queue()
    telem_queue = Queue()
    beam_gap_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    myGui = GUI(Queue(), Queue(), Queue(), Queue(), threading.Event(), server_ip)
    myGui.start()

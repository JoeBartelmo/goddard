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

import logging

MARS_EXIT_COMMAND = 'exit'

def start(client_queue_cmd, client_queue_log, client_queue_telem, server_ip):
    """
    Start graphical interface for client.

    Args:
        client_queue_in: queue to get telemetry and logging info
        client_queue_out: queue to communicate commands
        server_ip: server IP address for rtsp stream access
    """
    logger = logging.getLogger('mars_logging')
    logger.info('Creating GUI')
    root = tk.Tk()   # get root window
    
    #kill command destroys mars too
    def killMars():
        client_queue_cmd.put(MARS_EXIT_COMMAND)

    #explicitly close each widget, then destroy root
    def destroyCallback():
        logger.debug('GUI entering destroy callback...')
        result = tkMessageBox.askyesno('Leaving GUI, Should Mars be Disabled?', 'Leaving GUI, should Mars be Disabled?')

        if result:
            killMars()
        menu_.destroy() 
        mainApplication.close_()
        root.destroy()

    # define mainapp instance
    mainApplication = MainApplication(root, client_queue_cmd, client_queue_log, client_queue_telem, server_ip) 
    mainApplication.grid(column = 0, row = 0, sticky="nsew")
    # menu
    menu_ = TopMenu(root, '../gui/operations.json', client_queue_cmd, 'Commands')
    ### Add custom commands here
    menu_.add_menu_item('Refresh Streams', mainApplication.start_streams)
    ###
    menu_.finalize_menu_items()
    root.config(menu=menu_)

    # title and icon
    root.wm_title('Hyperloop Imaging Team')
    img = tk.PhotoImage('../gui/assets/rit_imaging_team.png')
    root.tk.call('wm', 'iconphoto', root._w, img)
    
    #call destroyCallback on clicking X
    root.protocol('WM_DELETE_WINDOW', destroyCallback)
     
    root.update()
    root.mainloop()

if __name__=='__main__':
    from Queue import Queue
    from ColorLogger import initializeLogger 

    logger = initializeLogger('./', logging.DEBUG, 'mars_logging', sout = True, colors = True)
    logger.debug('GUI is running independant of client, attempting to connect to server hyperlooptk1.student.rit.edu')

    cmd_queue = Queue()
    log_queue = Queue()
    telem_queue = Queue()
    server_ip = 'hyperlooptk1.student.rit.edu'

    start(cmd_queue, log_queue, telem_queue, server_ip)

    while not cmd_queue.empty():
        print cmd_queue.get()    

#!/usr/bin/env python
#
# @file "main"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/4/2016"
# @copyright "MIT"
#

import Tkinter as tk
import src.client.client_gui.VideoStream as VideoStream
import src.client.client_controller.MasterControl as MasterControl
import sys


class MainApplication(tk.Frame):
	#lets implement an argument interpreter; either it takes in a file that has configurations
	#(some object notation like JSON would probably be fine) or we could have a command line arg stuff
	#but that could get weird, i recommend a file interpretor
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.video_1 = VideoStream(self.parent, './assets/drop.avi')
        self.video_1.proc.start()

        self.video_2 = VideoStream(self.parent, './assets/drop.avi')
        self.video_2.proc.start()

        self.master_ctrl = MasterControl(self.parent, self.video_1, self.video_2)

        self.video_1.frame.grid(row=0, column=0, padx=5, pady=5)
        self.video_2.frame.grid(row=0, column=1, padx=5, pady=5)
        self.master_ctrl.frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        self.grid(sticky='e')


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).grid()
    root.resizable(width=False, height=False)
    root.mainloop()
    sys.exit()

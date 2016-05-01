#!/usr/bin/env python
#
# @file "client_gui.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#

import Tkinter as tk
from MasterWidget import MasterWidget
from VideoWidget import VideoWidget

class MainApplication(tk.Frame):
    def __init__(self, parent, src1, src2, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.video_1 = VideoWidget(self.parent, src1)
        self.video_1.proc.start()

        self.video_2 = VideoWidget(self.parent, src2)
        self.video_2.proc.start()

        self.master_ctrl = MasterWidget(self.parent, self.video_1, self.video_2)
        
        self.video_1.frame.grid(row=0, column=0, padx=5, pady=5)
        self.video_2.frame.grid(row=0, column=1, padx=5, pady=5)
        self.master_ctrl.frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        
        self.grid(sticky='e')


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root, 'drop.avi', 'drop.avi').grid()
    root.resizable(width=False, height=False)
    root.mainloop()


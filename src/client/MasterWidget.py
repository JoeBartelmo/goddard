#!/usr/bin/env python
# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys

class MasterWidget(tk.Frame):
    def __init__(self, parent, vid1, vid2):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)
        
        self.vid1 = vid1
        self.vid2 = vid2

        self.parent = parent

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.move_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)
        self.quit_button = tk.Button(self.frame, text='x', command=self.quit)

        self.slider = tk.Scale(self.frame, from_=0, to=100, orient='horizontal', length=200, command=self.slider_move)

        self.snap_start.grid(row=0, column=0)
        self.move_back.grid(row=0, column=1)
        self.pause_button.grid(row=0, column=2)
        self.play_button.grid(row=0, column=3)
        self.move_forward.grid(row=0, column=4)
        self.snap_current.grid(row=0, column=5)
        
        self.slider.grid(row=0, column=6)
        self.quit_button.grid(row=0, column=7)

    def play(self):
        if self.vid1.after_id is None:
            self.vid1.play()

        if self.vid2.after_id is None:
            self.vid2.play()

    def pause(self):
        self.vid1.pause()
        self.vid2.pause()

    def move_fwd(self):
        self.vid1.move_fwd()
        self.vid2.move_fwd()

    def move_bkwd(self):
        self.vid1.move_bkwd()
        self.vid2.move_bkwd()

    def move_current(self): 
        self.vid1.move_current()
        self.vid2.move_current()

    def move_start(self): 
        self.vid1.move_start()
        self.vid2.move_start()

    def slider_move(self, val):
        self.vid1.slider.set(val)
        self.vid2.slider.set(val)
        new_to = self.vid1.slider.config()['to'][-1]
        self.slider.config(to=new_to)

    def quit(self):
        self.vid1.quit()
        self.vid2.quit()
        #self.parent.destroy()
        sys.exit(0)


#!/usr/bin/env python
#
# @file "client_gui.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#

import numpy as np
from multiprocessing import Process, Queue, Pipe, Manager
from Queue import Empty
import cv2
import cv2.cv as cv
from PIL import Image, ImageTk
import time
import Tkinter as tk
import sys

class VideoStream(tk.Frame):
    def __init__(self, parent, src):
        self.frame = tk.Frame()
        self.manager = Manager()
        self.frames = self.manager.list()

        self.vidcap = cv2.VideoCapture(src)
        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.curr_frame = 0
        self.after_id = None
        
        self.proc = Process(target=self.image_capture)

        self.initial_im = tk.PhotoImage(file='test.png')
        self.image_label = tk.Label(self.frame, image=self.initial_im, height=self.height, width=self.width)
        self.image_label.grid(row=0, column=0, columnspan=6, padx=5, pady=5)

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.snap_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)

        self.slider = tk.Scale(self.frame, from_=0, to=100, orient='horizontal', \
                                length=250, command=self.slider_move)

        self.snap_start.grid(row=1, column=0)
        self.move_back.grid(row=1, column=1)
        self.pause_button.grid(row=1, column=2)
        self.play_button.grid(row=1, column=3)
        self.move_forward.grid(row=1, column=4)
        self.snap_current.grid(row=1, column=5)

        self.slider.grid(row=2, column=0, columnspan=6, sticky='w')

    def update_image(self):
        try:
            frame = self.frames[self.curr_frame]

            im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            a = Image.fromarray(im)
            b = ImageTk.PhotoImage(image=a)
            self.image_label.configure(image=b)
            self.image_label._image_cache = b  # avoid garbage collection
            self.frame.update()
        except IndexError:
            pass

    def image_capture(self):
        while True:
          try:
             flag, frame= self.vidcap.read()
             if not flag:
                break
             self.frames.append(frame)
             
          except:
             continue
    
    def play(self):
        self.slider.config(to=len(self.frames))
        self.slider.set(self.curr_frame)
        self.update_image()
        self.curr_frame += 1

        self.after_id = self.frame.after(33, self.play)

    def pause(self):
        if self.after_id is not None:
            self.frame.after_cancel(self.after_id)
        self.after_id = None

    def move_fwd(self):
        self.curr_frame += 30
        if self.curr_frame >= len(self.frames):
            self.curr_frame = len(self.frames) - 1
        self.update_image()
        self.slider.set(self.curr_frame)

    def move_bkwd(self):
        self.curr_frame -= 30
        if self.curr_frame <= 0:
            self.curr_frame = 0
        self.update_image()
        self.slider.set(self.curr_frame)

    def snap_current(self): 
        self.curr_frame = len(self.frames) - 1
        self.update_image()
        self.slider.set(self.curr_frame)

    def move_start(self): 
        self.curr_frame = 0
        self.update_image()
        self.slider.set(0)

    def slider_move(self, new_val):
        self.curr_frame = self.slider.get()
        self.update_image()

class MasterControl(tk.Frame):
    def __init__(self, parent, vid1, vid2):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)
        
        self.vid1 = vid1
        self.vid2 = vid2

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.snap_current)
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

    def snap_current(self): 
        self.vid1.snap_current()
        self.vid2.snap_current()

    def move_start(self): 
        self.vid1.move_start()
        self.vid2.move_start()

    def slider_move(self, val):
        self.vid1.slider.set(val)
        self.vid2.slider.set(val)
        new_to = self.vid1.slider.config()['to'][-1]
        self.slider.config(to=new_to)

    def quit(self):
        root.destroy()
        sys.exit(0)

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        self.video_1 = VideoStream(self.parent, 'drop.avi')
        self.video_1.proc.start()

        self.video_2 = VideoStream(self.parent, 'drop.avi')
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


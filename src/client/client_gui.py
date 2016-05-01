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
        self.frame.pack()
        self.manager = Manager()
        self.frames = self.manager.list()

        self.vidcap = cv2.VideoCapture(src)
        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.p = True
        self.curr_frame = 0
        
        self.proc = Process(target=self.image_capture)
        self._play = Process(target=self.play)

        self.after_id = None

        self.initial_im = tk.PhotoImage(file='test.png')
        self.image_label = tk.Label(self.frame, image=self.initial_im, height=self.height, width=self.width)
        self.image_label.pack(side='top')

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.snap_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)

        self.snap_start.pack(side='left')
        self.move_back.pack(side='left')
        self.pause_button.pack(side='left')
        self.play_button.pack(side='left')
        self.move_forward.pack(side='left')
        self.snap_current.pack(side='left')

    def update_image(self):
        frame = self.frames[self.curr_frame]

        im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  # avoid garbage collection
        self.frame.update()

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
        
        self.update_image()
        self.curr_frame += 1

        self.after_id = self.frame.after(33, self.play)

    def pause(self):
        self.frame.after_cancel(self.after_id)

    def move_fwd(self):
        self.curr_frame += 30
        if self.curr_frame >= len(self.frames):
            self.curr_frame = len(self.frames) - 1

    def move_bkwd(self):
        self.curr_frame -= 30
        if self.curr_frame <= 0:
            self.curr_frame = 0

    def snap_current(self): 
        self.curr_frame = len(self.frames) - 1

    def move_start(self): 
        self.curr_frame = 0

class MasterControl(tk.Frame):
    def __init__(self, parent, vid1, vid2):
        self.frame = tk.Frame()
        self.frame.pack()
        tk.Frame.__init__(self)
        
        self.vid1 = vid1
        self.vid2 = vid2

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.snap_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)
        self.quit_button = tk.Button(self, text='Quit', command=self.quit)

        self.snap_start.pack(side='left')
        self.move_back.pack(side='left')
        self.pause_button.pack(side='left')
        self.play_button.pack(side='left')
        self.move_forward.pack(side='left')
        self.snap_current.pack(side='left')
        self.quit_button.pack(side='right')

    def play(self):
        self.vid1.play()
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

        
        self.video_1.frame.pack(side='left')
        self.video_2.frame.pack(side='right')
        self.master_ctrl.frame.pack()
        
        self.pack(side="right", fill="both", expand=True)


if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
    sys.exit()


#!/usr/bin/env python
#
# @file "client_gui.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#

import numpy as np
from multiprocessing import Process, Queue
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
        self.queue = Queue()

        self.vidcap = cv2.VideoCapture(src)
        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.initial_im = tk.PhotoImage(file='test.png')
        self.image_label = tk.Label(self.frame, image=self.initial_im, height=self.height, width=self.width)
        self.image_label.pack(side='top')

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.move_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)

        self.snap_start.pack(side='left')
        self.move_back.pack(side='left')
        self.pause_button.pack(side='left')
        self.play_button.pack(side='left')
        self.move_forward.pack(side='left')
        self.snap_current.pack(side='left')

        self.p = True
        
        self.proc = Process(target=self.image_capture)

    def update_image(self):
        frame = self.queue.get()

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
             self.queue.put(frame)
          except:
             continue
    
    def play(self):
        self.p = True
        while self.p is True:
            try:
                self.update_image()

                s = time.time()
                while time.time() - s < 1/30.0:
                    pass
            except:
                continue

    def pause(self):
        self.p = False

    def move_fwd(self):
        pass
    def move_bkwd(self):
        pass
    def move_current(self):
        pass
    def snap_current(self): 
        pass
    def move_start(self): 
        pass


class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.video_1 = VideoStream(self.parent, 'drop.avi')
        self.video_1.frame.pack(side='left', fill='both', expand=1)
        self.video_1.proc.start()
        self.video_2 = VideoStream(self.parent, 'drop.avi')
        self.video_2.frame.pack(side='left', fill='both', expand=1)
        self.video_2.proc.start()

        self.quit_button = tk.Button(self, text='Quit', command=self.quit)
        self.quit_button.pack()
        self.pack(side="right", fill="both", expand=True)
        
    def quit(self):
        root.destroy()
        sys.exit(0)
        

if __name__ == "__main__":
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()
    sys.exit()


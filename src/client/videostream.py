#!/usr/bin/env python

# @file "videostream.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#

import numpy as np
from multiprocessing import Process, Manager
import cv2
from PIL import Image, ImageTk
import Tkinter as tk

class VideoStream():
    def __init__(self, videoCaptureSource):
        self.frame = tk.Frame()
        self.manager = Manager()
        self.frames = self.manager.list()

        self.vidcap = videoCaptureSource
        self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3); #internal buffer will now store only 3 frames; adjust as needed

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

        self.slider = tk.Scale(self.frame, from_=0, to=100, orient='horizontal', length=250, command=self.slider_move)

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
                continue
                #this we have to adjust -- implement buffer
             self.frames.append(frame)
             
          except:
             continue
    
    def play(self):
        #self.slider.config(to=len(self.frames))
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


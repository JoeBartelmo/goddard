#!/usr/bin/env python
# Copyright MIT
# Primary Author: Nathan Dileas

from multiprocessing import Process, Queue, Manager
import cv2
import cv2.cv as cv
from PIL import Image, ImageTk
import Tkinter as tk
import time

class VideoWidget(tk.Frame):
    vidcap_isClosed = False
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

        self.initial_im = tk.PhotoImage(file='blank_256x240.png')
        self.image_label = tk.Label(self.frame, image=self.initial_im, height=self.height, width=self.width)
        self.image_label.grid(row=0, column=0, columnspan=6, padx=5, pady=5)

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=self.move_fwd)
        self.move_back = tk.Button(self.frame, text='<<', command=self.move_bkwd)
        self.snap_current = tk.Button(self.frame, text='|>', command=self.move_current)
        self.snap_start = tk.Button(self.frame, text='<|', command=self.move_start)

        self.slider = tk.Scale(self.frame, from_=0, to=100, orient='horizontal', \
                                length=250, command=self.slider_move)

        self.frame_rate_text = tk.StringVar()
        self.frame_rate_display = tk.Label(self.frame, textvariable=self.frame_rate_text)
        self.frame_rate_display.grid(row=1, column=6)

        self.snap_start.grid(row=1, column=0)
        self.move_back.grid(row=1, column=1)
        self.pause_button.grid(row=1, column=2)
        self.play_button.grid(row=1, column=3)
        self.move_forward.grid(row=1, column=4)
        self.snap_current.grid(row=1, column=5)

        self.slider.grid(row=2, column=0, columnspan=6, sticky='w')

    def update_image(self):
        if self.curr_frame < len(self.frames):
            frame = self.frames[self.curr_frame]
        else:
            if len(self.frames) == 0:
                return
            frame = self.frames[-1]
            

        im = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  # avoid garbage collection
        self.frame.update()
        
    def image_capture(self):
        while self.vidcap:
            flag, frame= self.vidcap.read()
            if not flag:
                continue
            self.frames.append(frame)
           
    
    def play(self, t=0):
        self.frame_rate_text.set('Framerate: %2.0f' % (1 / (100* float(time.clock() - t))))
        self.slider.config(to=len(self.frames))
        self.slider.set(self.curr_frame)
        self.update_image()
        self.curr_frame += 1
        
        self.after_id = self.frame.after(10, self.play, time.clock())   # TODO make constant

    def pause(self):
        tic = time.clock()
        while time.clock() - tic < 5:
            if self.after_id is not None:
                self.frame.after_cancel(self.after_id)
                self.after_id = None
                break

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

    def move_current(self): 
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

    def quit(self):
        self.proc.terminate()
        self.vidcap.release()
        

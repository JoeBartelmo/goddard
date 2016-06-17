#!/usr/bin/env python
# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
from multiprocessing import Queue
from VideoWidget import VideoWidget

import img_rms

class MasterWidget(tk.Frame):
    def __init__(self, parent, videos):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)
        
        do_rms = lambda: img_rms.do(self.raw_vid.queue, self.rms.queue, self.output.queue)

        self.raw_vid.VideoWidget(parent).grid(row=0, column=0)
        self.output.VideoWidget(parent, get_output).grid(row=0, column=1)
        self.rms.VideoWidget(parent, do_rms).grid(row=1, column=0)
        self.pumpkin.VideoWidget(parent, do_pumpkin).grid(row=1, column=1)
        
        self.parent = parent

        self.vidcap = cv2.VideoCapture(src)
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3)
        #internal buffer will now store only 3 frames; adjust as needed

        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.proc = Process(target=self.image_capture)

        self.pause_button = tk.Button(self.frame, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self.frame, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self.frame, text='>>', command=lambda:self.move(0))
        self.move_back = tk.Button(self.frame, text='<<', command=lambda:self.move(0))
        self.snap_current = tk.Button(self.frame, text='|>', command=lambda:self.move(0))
        self.snap_start = tk.Button(self.frame, text='<|', command=lambda:self.move(0))
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

    def image_capture(self):
        while self.vidcap:
            flag, frame= self.vidcap.read()
            if not flag:
                break

            img = demosaic(frame)
            img_col = color_correct(img)

            self.raw_vid.queue.put(frame)  # TODO change to img_col

    def demosaic(input_im):
        pass

    def color_correct(input_im):
        return cv2.cvtColor(input_im, cv2.COLOR_BGR2RGB)

    def play(self):
        #for vid in self.vids:
        #    vid.update_image()

        self.raw_vid.update_image()
        self.rms.update_image()
        self.pumpkin.update_image()
        self.output.update_image()

        self.after_id = self.frame.after(10, self.play)   # TODO make constant

    def pause(self):
        if self.after_id is not None:
            self.frame.after_cancel(self.after_id)
            self.after_id = None

    def move(self, t):
        pass

    def update_slider(self, new_val):
        self.slider.config(to=len(self.frames))
        self.slider.set(self.curr_frame)

    def slider_move(self, val):
        pass

    def quit(self):
        for vid in self.vids:
            vid.quit()
        sys.exit(0)


#!/usr/bin/env python
#
# @file "main"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/4/2016"
# @copyright "MIT"
#

import Tkinter as tk
import sys
#TODO: deserialize streams into RTSP clients (assume regular videocapture class for non-rtsp stream types
from src.client.rtsp_client import RTSPClient


class MasterControl(tk.Frame):
    def __init__(self, parent, streams):
        self.frame = tk.Frame()
        tk.Frame.__init__(self)

        if isinstance(streams, list):
            self.streams = streams
        else:
            self.streams = list(streams)

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
        for stream in self.streams:
            if stream is not None and stream.isOpened() and stream.after_id is None:
                stream.play()

    def pause(self):
        for stream in self.streams:
            if stream is not None and stream.isOpened():
                stream.pause()

    def move_fwd(self):
        for stream in self.streams:
            if stream is not None and stream.isOpened():
                stream.move_fwd()

    def move_bkwd(self):
        for stream in self.streams:
            if stream is not None and stream.isOpened():
                stream.move_bkwd()

    def snap_current(self):
        for stream in self.streams:
            if stream is not None and stream.isOpened():
                stream.snap_current()

    def move_start(self):
        for stream in self.streams:
            if stream is not None and stream.isOpened():
                stream.move_start()

    # def slider_move(self, val):
    #     self.vid1.slider.set(val)
    #     self.vid2.slider.set(val)
    #     new_to = self.vid1.slider.config()['to'][-1]
    #     self.slider.config(to=new_to)

    def quit(self):
        for stream in self.streams:
            if stream is not None and stream.after_id is None:
                stream.pause ()
        sys.exit(0)

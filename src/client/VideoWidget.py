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
    def __init__(self, parent, p=None, frame_size=(500,300)):
        tk.Frame.__init__(self, parent,width=500,height=375, bd=2, relief='groove')
        self.parent = parent

        self.queue = Queue()
        self.proc = p

	self.frame_size = frame_size

        self.initial_im = tk.PhotoImage(file='client/assets/blank_256x240.png')
        self.image_label = tk.Label(self, image=self.initial_im, height=300, width=500)
        self.image_label.grid(row=0, column=0, padx=5, pady=5)

    def update_image(self):
        frame = self.queue.get()

        frame_resized = cv2.resize(frame, self.frame_size)
        a = Image.fromarray(frame_resized)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b, height=300, width=500)
        self.image_label._image_cache = b  # avoid garbage collection
        self.update()


#!/usr/bin/env python
# Copyright MIT
# Primary Author: Nathan Dileas

from multiprocessing import Process, Queue, Manager
import cv2
import cv2.cv as cv
from PIL import Image, ImageTk
import Tkinter as tk
import time

class VideoWidget:
    def __init__(self, parent, p=None):
        self.frame = tk.Frame(parent)
        self.parent = parent

        self.queue = Queue()
        self.proc = p

        self.initial_im = tk.PhotoImage(file='assets/blank_256x240.png')
        self.image_label = tk.Label(self.frame, image=self.initial_im, height=240, width=256)
        self.image_label.grid(row=0, column=0, padx=5, pady=5)

    def update_image(self):
        frame = self.queue.get()

        a = Image.fromarray(frame)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  # avoid garbage collection
        self.frame.update()


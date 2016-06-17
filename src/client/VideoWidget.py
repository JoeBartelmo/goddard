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
    def __init__(self, parent, p=None):
        self.frame = tk.Frame()
        self.parent = parent

        self.queue = Queue()
        if p is not None:
            self.proc = Process(target=p)

        self.image_label = tk.Label(self.frame)
        self.image_label.grid(row=0, column=0, padx=5, pady=5)

    def update_image(self):
        frame = self.queue.get()

        a = Image.fromarray(frame)
        b = ImageTk.PhotoImage(image=a)
        self.image_label.configure(image=b)
        self.image_label._image_cache = b  # avoid garbage collection
        self.frame.update()

    def quit(self):
        pass

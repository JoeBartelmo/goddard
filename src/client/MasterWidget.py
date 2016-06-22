# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
from multiprocessing import Queue, Process
from VideoWidget import VideoWidget
import cv2

import img_rms
import stealth_pumpkin
import highlight

def demosaic(input_im):
    #orig_gray = cv2.cvt2Color(input_im, cv2.COLOR_RGB2GRAY)  # THIS STEP IS NECESARY, check w/ kristina
    #demosaiced = cv2.cvt2Color(orig_gray, cv2.COLOR_BAYER_GR2RGB)
    return input_im

def color_correct(input_im):
    #return cv2.cvtColor(input_im, cv2.COLOR_BGR2RGB)
    return input_im

class MasterWidget(tk.Frame):
    def __init__(self, parent, source):
        tk.Frame.__init__(self, parent,width=768, height=576)
        self.parent = parent

        self.init_ui()
        
        self.raw_q_1 = Queue()
        self.raw_q_2 = Queue()
        self.raw_q_3 = Queue()
        self.highlight_q = Queue()

        do_rms = lambda: img_rms.script(self.raw_q_1, self.rms.queue, self.highlight_q)
        do_pump = lambda: stealth_pumpkin.script(self.raw_q_2, self.pumpkin.queue, self.highlight_q)
        do_highlight = lambda: highlight.script(self.raw_q_3, self.highlight_q, self.output.queue)

        self.rms.proc = Process(target=do_rms)
        self.pumpkin.proc = Process(target=do_pump)
        self.output.proc = Process(target=do_highlight)
        self.proc = Process(target=self.image_capture)

        self.vidcap = cv2.VideoCapture('drop.avi')  # FIXME should be source
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3) # TODO check docs on this

        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.after_id = None

    def init_ui(self):
        self.raw_vid = VideoWidget(self)
        self.output = VideoWidget(self)
        self.rms = VideoWidget(self)
        self.pumpkin = VideoWidget(self)

        self.raw_vid.frame.grid(row=0, column=0, columnspan=2)
        self.output.frame.grid(row=0, column=1, columnspan=2)
        self.pumpkin.frame.grid(row=0, column=2, columnspan=2)
        self.rms.frame.grid(row=0, column=3, columnspan=2)

        self.image_captur = tk.Button(self, text='Image Capture', command=self.image_capture)

        self.pause_button = tk.Button(self, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self, text='>>', command=lambda:self.move(0))
        self.move_back = tk.Button(self, text='<<', command=lambda:self.move(0))
        self.snap_current = tk.Button(self, text='|>', command=lambda:self.move(0))
        self.snap_start = tk.Button(self, text='<|', command=lambda:self.move(0))

        self.snap_start.grid(row=1, column=0)
        self.move_back.grid(row=1, column=1)
        self.pause_button.grid(row=1, column=2)
        self.play_button.grid(row=1, column=3)
        self.move_forward.grid(row=1, column=4)
        self.snap_current.grid(row=1, column=5)
        self.image_captur.grid(row=1, column=6)
        
        self.slider = tk.Scale(self, from_=0, to=100, orient='horizontal', length=200, command=self.slider_move)

        self.slider.grid(row=2, column=0)

    def start(self):
        self.proc.start()
        self.rms.proc.start()
        self.pumpkin.proc.start()
        self.output.proc.start()  

    def image_capture(self, count=0):
        flag, frame= self.vidcap.read()

        img = demosaic(frame)
        img_col = color_correct(img)

        self.raw_q_1.put(frame)  # TODO change to img_col 
        self.raw_q_2.put(frame)   # TODO implement counter
        self.raw_q_3.put(frame)
        self.raw_vid.queue.put(frame)

        count += 1
        self.frame.after(10, self.image_capture, count)

    def play(self):
        #for vid in self.vids:
        #    vid.update_image()

        #if self.raw_vid.queue.qsize() == self.rms.queue.qsize() ==self.pumpkin.queue.qsize() == self.output.queue.qsize():
        #print self.raw_vid.queue.qsize(), self.rms.queue.qsize(), self.pumpkin.queue.qsize(), self.output.queue.qsize()
        self.raw_vid.update_image()
        self.rms.update_image()
        self.pumpkin.update_image()
        #self.output.update_image()

        self.frame.after(25, self.play)   # TODO make constant

    def pause(self):
        if self.after_id is not None:
            self.frame.after_cancel(self.after_id)
            self.after_id = None

    def move(self, t):
        # t in seconds
        self.vidcap.set(0,t*1000)

    def update_slider(self, new_val):
        self.slider.config(to=len(self.frames))
        self.slider.set(self.curr_frame)

    def slider_move(self, val):
        pass

    def quit(self):
        self.frame.quit()
        sys.exit(0)


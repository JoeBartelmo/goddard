# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
from multiprocessing import Queue, Process
from VideoWidget import VideoWidget
import cv2
import time

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
        tk.Frame.__init__(self, parent,width=1020, height=700, bd=2, relief='groove')
        self.parent = parent

        self.init_ui()
        
        self.raw_q_1 = Queue()
        self.raw_q_2 = Queue()
        self.highlight_q = Queue()

        do_rms = lambda: img_rms.script(self.raw_q_1, self.rms.queue)
        do_pump = lambda: stealth_pumpkin.script(self.raw_q_2, self.pumpkin.queue)

        self.rms.proc = Process(target=do_rms)
        self.pumpkin.proc = Process(target=do_pump)
        self.proc = Process(target=self.image_capture)

        self.vidcap = cv2.VideoCapture(0)#'/home/nathan/python/PyDetect/src/client/assets/drop.avi')  # FIXME should be source
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3) # TODO check docs on this

        fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
        self.vidout = cv2.VideoWriter('output.avi',fourcc, 45.0, (480,848))

        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.width = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.height = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        self.after_id = None

    def init_ui(self):
        self.raw_vid = VideoWidget(self)
        self.rms = VideoWidget(self)
        self.pumpkin = VideoWidget(self)

        self.raw_vid.grid(row=0, column=0, columnspan=3, sticky='nw')
        self.pumpkin.grid(row=1, column=0, columnspan=3, sticky='sw')
        self.rms.grid(row=0, column=4, columnspan=3, sticky='se')

        self.pause_button = tk.Button(self, text=u'\u23F8', command=self.pause)
        self.play_button = tk.Button(self, text=u'\u25B6', command=self.play)
        self.move_forward = tk.Button(self, text='>>', command=lambda:self.move(0))
        self.move_back = tk.Button(self, text='<<', command=lambda:self.move(0))
        self.snap_current = tk.Button(self, text='|>', command=lambda:self.move(0))
        self.snap_start = tk.Button(self, text='<|', command=lambda:self.move(0))

        self.snap_start.grid(row=2, column=0)
        self.move_back.grid(row=2, column=1)
        self.pause_button.grid(row=2, column=2)
        self.play_button.grid(row=2, column=3)
        self.move_forward.grid(row=2, column=4)
        self.snap_current.grid(row=2, column=5)
        
    def start(self):
        self.proc.start()
        self.rms.proc.start()
        self.pumpkin.proc.start()

    def image_capture(self):
        
        while True:
            while self.raw_q_1.qsize() < 100:
                flag, frame = self.vidcap.read()

                if not flag:
                    return

                img = demosaic(frame)
                img_col = color_correct(img)

                self.raw_q_1.put(frame)
                self.raw_q_2.put(frame)
                self.raw_vid.queue.put(frame)  # TODO save also
                #self.vidout.write(frame)

            time.sleep(1)

    def play(self):
        #print self.raw_vid.queue.qsize(), self.rms.queue.qsize(), self.pumpkin.queue.qsize()#, self.output.queue.qsize()

        if self.raw_vid.queue.qsize() == 0:
            return

        self.raw_vid.update_image()
        self.rms.update_image()
        self.pumpkin.update_image()

        self.after_id = self.after(25, self.play)   # TODO make constant

    def pause(self):
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def move(self, t):
        # t in seconds
        self.vidcap.set(0,t*1000)

    def quit_(self):
        
        self.proc.terminate()
        self.vidcap.release()
        self.vidout.release()
        self.rms.proc.terminate()
        self.pumpkin.proc.terminate()
        self.quit()
        sys.exit(0)


# Copyright MIT
# Primary Author: Nathan Dileas

import Tkinter as tk
import sys
from multiprocessing import Queue, Process
from VideoWidget import VideoWidget
import cv2
import time

import stealth_pumpkin

def demosaic(input_im):
    #orig_gray = cv2.cvt2Color(input_im, cv2.COLOR_RGB2GRAY)  # THIS STEP IS NECESARY, check w/ kristina
    #demosaiced = cv2.cvt2Color(orig_gray, cv2.COLOR_BAYER_GR2RGB)
    return input_im

def color_correct(input_im):
    #return cv2.cvtColor(input_im, cv2.COLOR_BGR2RGB)
    return input_im

class VideoStream(tk.Frame):
    def __init__(self, parent, source, name, frame_size=(320, 240)):
        tk.Frame.__init__(self, parent, padx=3, pady=3, bd=2, relief='groove')
        self.parent = parent

        self.frame_size = frame_size
        self.name = name
        self.init_ui()
        
        self.raw_q_1 = Queue()

        do_pump = lambda: stealth_pumpkin.script(self.raw_q_1, self.pumpkin.queue)

        self.pumpkin.proc = Process(target=do_pump)
        self.proc = Process(target=self.image_capture)

        self.vidcap = cv2.VideoCapture(source)
        #self.vidcap.set(cv2.cv.CV_CAP_PROP_BUFFERSIZE, 3) # TODO check docs on this

        self.fps = self.vidcap.get(cv2.cv.CV_CAP_PROP_FPS)
        self.fwidth = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
        self.fheight = int(self.vidcap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

        fourcc = cv2.cv.CV_FOURCC('M','J','P','G')
        self.vidout = cv2.VideoWriter('output.avi',fourcc, 45.0, (self.fheight,self.fwidth))

        self.after_id = None
        self.proc.start()

    def init_ui(self):
        self.raw_vid = VideoWidget(self, self.frame_size)
        self.pumpkin = VideoWidget(self, self.frame_size)

        self.pumpkin.grid(row=0, column=0, sticky='nw', columnspan=2)
        self.raw_vid.grid(row=0, column=0, sticky='nw', columnspan=2)
        
        self.show_pump = tk.IntVar()

        tk.Checkbutton(self, text="Pumpkin", variable=self.show_pump, command=self.show).grid(row=1,column=1, sticky='se')
        tk.Label(self, text=self.name, justify='left').grid(row=1, column=0, sticky='sw')

    def show(self):
        if self.show_pump.get() == 0:
            self.raw_vid.tkraise()
        elif self.show_pump.get() == 1:
            self.pumpkin.tkraise()
        
    def start(self):
        self.proc.start()
        self.pumpkin.proc.start()

    def image_capture(self): 
        while True:
            while self.raw_vid.queue.qsize() < 100:
                flag, frame = self.vidcap.read()

                if not flag:
                    return

                img = demosaic(frame)
                img_col = color_correct(img)

                self.raw_q_1.put(frame)
                self.raw_vid.queue.put(frame)  # TODO save also
                #self.vidout.write(frame)

    def play(self):
        print self.raw_vid.queue.qsize(), self.rms.queue.qsize(), self.pumpkin.queue.qsize()#, self.output.queue.qsize()

        if self.raw_vid.queue.qsize() == 0:
            return

        self.raw_vid.update_image()
        self.pumpkin.update_image()

        self.after_id = self.after(25, self.play)   # TODO make constant

    def pause(self):
        for i in range(50):
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None

    def move(self, t):
        self.vidcap.set(0,t*1000)

    def quit_(self):
        
        self.proc.terminate()
        self.pumpkin.proc.terminate()
        self.vidcap.release()
        self.vidout.release()
        self.quit()
        sys.exit(0)

if __name__=='__main__':
    root = tk.Tk()
    VideoStream(root).grid()
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()


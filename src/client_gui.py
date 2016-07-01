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
import argparse

from client.json_serializable_object import SerializableClient
from client.TelemetryWidget import TelemetryWidget
from client.MasterWidget import MasterWidget
from client.ControlWidget import ControlWidget
from client.VideoStream import VideoStream

class MainApplication(tk.Frame):
    def __init__(self, parent, args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.serializedClient = SerializableClient(args.json_file)

        self.init_ui()

        self.start_streams()

    def init_ui(self):
        self.streams = []

        l = VideoStream(self, 0, 'Left', num=0)
        l.grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nw')
        self.streams.append(l)

        c = VideoStream(self, 'drop.avi', 'Center', num=1)
        c.grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky='nw')
        self.streams.append(c)

        r = VideoStream(self, 'drop.avi', 'Right', frame_size=(640,480), num=2)
        r.grid(row=1, column=0, columnspan=4, rowspan=2, padx=5, pady=5, sticky='nw')
        self.streams.append(r)

        buttons = ['Left', 'Center', 'Right']

        col = 0
        self.stream_active = tk.IntVar()
        for text in buttons:
            b = tk.Radiobutton(self, text=text, variable=self.stream_active, value=col,\
                         command=self.show_stream)
            b.grid(row=3, column=col, sticky='nw')
            col += 1

        self.master_w = MasterWidget(self, self.streams)
        self.master_w.grid(row=3, column=3, padx=5, pady=5, sticky='nw')

        self.telemetry_w = TelemetryWidget(self)
        self.telemetry_w.grid(row=0, column=4, rowspan=2, padx=5, pady=5, sticky='nw')

        self.command_w = ControlWidget(self)
        self.command_w.grid(row=2, column=4, rowspan=4, padx=5, pady=5, sticky='nw')

        self.grid(sticky='e')

    def start_streams(self):
        for stream in self.streams:
            stream.start()   # start grabbing frames

    def show_stream(self):
        for s in self.streams:
            s.grid_forget()

        if self.stream_active.get() == 0:  # left focus
            self.streams[0].raw_vid.image_label.configure(width=640,height=480)
            self.streams[0].pumpkin.image_label.configure(width=640,height=480)
            self.streams[0].grid(row=1, column=0, columnspan=4, rowspan=2, padx=5, pady=5, sticky='nw')

            self.streams[1].raw_vid.image_label.configure(width=320,height=240)
            self.streams[1].pumpkin.image_label.configure(width=320,height=240)
            self.streams[1].grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nw')

            self.streams[2].raw_vid.image_label.configure(width=320,height=240)
            self.streams[2].pumpkin.image_label.configure(width=320,height=240)
            self.streams[2].grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky='nw')
                
        elif self.stream_active.get() == 1:  # center focus
            self.streams[1].raw_vid.image_label.configure(width=640,height=480)
            self.streams[1].pumpkin.image_label.configure(width=640,height=480)
            self.streams[1].grid(row=1, column=0, columnspan=4, rowspan=2, padx=5, pady=5, sticky='nw')


            self.streams[0].raw_vid.image_label.configure(width=320,height=240)
            self.streams[0].pumpkin.image_label.configure(width=320,height=240)
            self.streams[0].grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nw')


            self.streams[2].raw_vid.image_label.configure(width=320,height=240)
            self.streams[2].pumpkin.image_label.configure(width=320,height=240)
            self.streams[2].grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky='nw')

        elif self.stream_active.get() == 2:  # right focus
            self.streams[2].raw_vid.image_label.configure(width=640,height=480)
            self.streams[2].pumpkin.image_label.configure(width=640,height=480)
            self.streams[2].grid(row=1, column=0, columnspan=4, rowspan=2, padx=5, pady=5, sticky='nw')


            self.streams[0].raw_vid.image_label.configure(width=320,height=240)
            self.streams[0].pumpkin.image_label.configure(width=320,height=240)
            self.streams[0].grid(row=0, column=0, columnspan=2, padx=5, pady=5, sticky='nw')


            self.streams[1].raw_vid.image_label.configure(width=320,height=240)
            self.streams[1].pumpkin.image_label.configure(width=320,height=240)
            self.streams[1].grid(row=0, column=2, columnspan=2, padx=5, pady=5, sticky='nw')
        
        self.update()

def main(args):
    root = tk.Tk()
    MainApplication(root, args)
    #root.resizable(width=False, height=False)
    root.update()
    print root.winfo_height(), root.winfo_width()
    root.mainloop()
    sys.exit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('json_file', type=str, help='JSON file for stream setup')
    args = parser.parse_args()

    if args.json_file.split('.')[-1] is not 'json':
        print 'Not a valid .json file extension'

    main(args)

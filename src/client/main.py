#!/usr/bin/env python
#
# @file "main"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/4/2016"
# @copyright "MIT"
#

import Tkinter
import sys
import argparse

from src.client.videostream import VideoStream
from src.client.client_controller import MasterControl
from src.client.json_serializable_object import SerializableClient
from src.client.TelemetryWidget import TelemetryWidget

class MainApplication(Tkinter.Frame):
	def __init__(self, parent, *args, **kwargs):
		Tkinter.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		#FIXME: Currently assumes that args will only be the file path
		self.serializedClient = SerializableClient(args[0])

		self.master_ctrl = MasterControl(self.parent, self.serializedClient.streams)
        self.telemetry_w = TelemetryWidget(self.parent, telemtry_stream)

		for stream in self.serializedClient.streams:
			stream.grid(row=0, column=0, padx=5, pady=5)

		self.master_ctrl.frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
        self.telemetry_w.frame.grid(row=2, column=0, columnspan=2, padx=5, pady=5)
		self.grid(sticky='e')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('json_file', type=str, help='JSON file for stream setup')
    args = parser.parse_args()

    if args.json_file.split('.')[-1] is not 'json':
         print 'Not a valid .json file extension'

	root = Tkinter.Tk()
	MainApplication(root, args).grid()
	root.resizable(width=False, height=False)
	root.mainloop()
	sys.exit()

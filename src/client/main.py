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
import argparse#TODO: Use argparse here to accept a json file

from src.client.videostream import VideoStream
from src.client.client_controller import MasterControl
from src.client.json_serializable_object import SerializableClient


class MainApplication(Tkinter.Frame):
	def __init__(self, parent, *args, **kwargs):
		Tkinter.Frame.__init__(self, parent, *args, **kwargs)
		self.parent = parent

		#FIXME: Currently assumes that args will only be the file path
		self.serializedClient = SerializableClient(args[0])

		self.master_ctrl = MasterControl(self.parent, self.serializedClient.streams)

		for stream in self.serializedClient.streams:
			stream.grid(row=0, column=0, padx=5, pady=5)

		self.master_ctrl.frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5)
		self.grid(sticky='e')


if __name__ == "__main__":
	root = Tkinter.Tk()
	MainApplication(root).grid()
	root.resizable(width=False, height=False)
	root.mainloop()
	sys.exit()

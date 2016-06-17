#!/usr/bin/env python
#
# @file "json_serializable_object"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/5/2016"
# @copyright "MIT"
#

import json
from src.client.pydetect_exception import PyDetectException

"""
Object Structure:
[
	{
		type: required String [possible values: rtsp, camera, file]
		source: required String [rtsp ip address, or camera index, or file location]
		port: (required if RTSP) integer
		location: optional String (rtsp location of file)
	},
	{
		"type" : "rtsp",
		"source" : "192.168.1.1",
		"port" : 564,
		"location" : "/dir/videofile.mp4"
	},
	{
		"type" : "file",
		"source" : "./drop.avi"
	},
	...
]

"""
class SerializableClient:
	streams = []

	def __init__(self, file_location):
		self.from_JSON(file_location)

	def to_JSON(self):
		return json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)

	def from_JSON(self, file_location):
		with open(file_location) as data_file:
			data = json.load(data_file)
			if isinstance(data, list):
				for stream_object in data:
					self.verify_stream_data(stream_object)
					self.streams.append(stream_object)
			else:
				self.verify_stream_data(data)
				self.streams.append(data)

	def verify_stream_data(self, data):
		if data is not None and data.source is not None and data.type is not None:
			if data.type is "rtsp" and data.port is None:
				raise PyDetectException("No port on RTSP stream: " + data)
			return True
		raise PyDetectException("No port on RTSP stream: " + data)

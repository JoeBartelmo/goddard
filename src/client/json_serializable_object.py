#!/usr/bin/env python
#
# @file "json_serializable_object"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "5/5/2016"
# @copyright "MIT"
#

import json
import cv2
from pydetect_exception import PyDetectException
#from rtsp_client import RTSPClient

SERVER = ''

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
class SerializableClient(object):
    input_data = []
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
                    stream = self.assign_stream_object(data)
                    self.input_data.append(stream_object)
            else:
                self.verify_stream_data(data)
                stream = self.assign_stream_object(data)
                self.input_data.append(data)

    def verify_stream_data(self, data):
        if data is not None and 'source' in data.keys() and 'type' in data.keys():
            if data['type'] is "rtsp" and data['port'] is None:
                raise PyDetectException("No port on RTSP stream: " + data)
            return True
        raise PyDetectException("No port on RTSP stream: " + data)

    def assign_stream_object(self, data):
        if data['type'] is "rtsp":
            # TODO make it be an rtsp client instance
            # return RTSPClient(SERVER, data['port'], data['location'])
            self.streams.append(cv2.VideoCapture('rtsp://%s:%s/' % (data['source'], data['port'])))
        else:
            self.streams.append(cv2.VideoCapture(data['source']))

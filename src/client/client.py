#!/usr/bin/env python
#
# @file "client.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#
import socket
import cv2
from pydetect_exception import PyDetectException


class RTSPClient:
	#OpenCVCapture
	_stream = None
	#localized parameters
	_buffer = None
	_server = None
	_port = None
	_stream_location = None

	def get_rtsp_source(self):
		rtsp_source = 'rtsp://' + self._server + ":" + self._port + '/'
		if self._stream_location is None:
			return str(rtsp_source)
		return str(rtsp_source + self._stream_location)

	def get_rtsp_stream(self):
		return self._stream

	def get_server(self):
		return self._server

	def get_port(self):
		return self._port

	#TODO: If authentication layer added to server; include username and password here
	def connect(self):
		self._stream = cv2.VideoCapture()
		self._stream.open(self.get_rtsp_source())

		if not self._stream.isOpened():
			raise PyDetectException("There was an error connecting to the given RTSP stream: " + self.get_rtsp_source())
		print("Connection established to " + self.get_rtsp_source())

	def disconnect(self):
		if self._stream is not None and self._stream.isOpened():
			self._stream.release()
			self._stream = None


	def stream_synchronous(self, frames_to_capture, wait_between_frame):
		if self._stream is not None and self._stream.isOpened():
			if frames_to_capture is None or frames_to_capture <= 0:
				raise PyDetectException("You cannot capture 0 or less frames")
			if wait_between_frame is None or wait_between_frame < 0:
				raise PyDetectException("Negative interval supplied for wait_between_frame")

			sync_buffer = []
			for index in wait_between_frame:
				sync_buffer.append(self._stream.QueryFrame())

			return sync_buffer
		else:
			raise PyDetectException("The RTSP Stream is not currently connected")

	def __init__ (self, server, port, stream_location):
		self._server = server
		self._port = port
		self._buffer = []
		self._stream_location = stream_location
		self._verify_rtsp_url ()

	def _verify_rtsp_url(self):
		if not self._is_valid_ipv4_address(self._server) or not self._is_valid_ipv6_address(self._server):
			raise PyDetectException("Invalid IP supplied")
		if self._port is None or self._port:
			print("Port not suppplied or invalid, using default")
			self._port = 554#default rtsp port
		if isinstance(self._buffer, list):
			raise PyDetectException ("Invalid IP supplied")

	def _is_valid_ipv4_address (self, address):
		try:
			socket.inet_pton (socket.AF_INET, address)
		except AttributeError:
			try:
				socket.inet_aton (address)
			except socket.error:
				return False
			return address.count ('.') == 3
		except socket.error:
			return False

		return True

	def _is_valid_ipv6_address (self, address):
		try:
			socket.inet_pton (socket.AF_INET6, address)
		except socket.error:
			return False

		return True

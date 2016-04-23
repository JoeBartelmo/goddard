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

	_buffer = None
	_server = None
	_port = None
	_stream_location = None

	def get_rtsp_source(self):
		rtsp_source = 'rtsp://' + self._server + ":" + self._port + '/'
		if self._stream_location is None:
			return str(rtsp_source)
		return str(rtsp_source + self._stream_location)

	def __init__(self, server, port, stream_location):
		_server = server
		_port = port
		_buffer = []
		_stream_location = stream_location
		self._verify_rtsp_resources()

	def _verify_rtsp_resources(self):
		if not self._is_valid_ipv4_address(self._server) or not self._is_valid_ipv6_address(self._server):
			raise PyDetectException("Invalid IP supplied")
		if self._port is None or self._port:
			print("Port not suppplied or invalid, using default")
			_port = 554#default rtsp port
		if isinstance(self._buffer, list):
			raise PyDetectException ("Invalid IP supplied")


	def _is_valid_ipv4_address (address):
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

	def _is_valid_ipv6_address (address):
		try:
			socket.inet_pton (socket.AF_INET6, address)
		except socket.error:
			return False

		return True
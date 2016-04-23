#!/usr/bin/env python
#
# @file "PyDetectException"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"
# @date "4/23/2016"
# @copyright "MIT"
#


class PyDetectException(Exception):

	def __init__(self, value):
		self.value = value

	def __str__(self):
		return repr(self.value)

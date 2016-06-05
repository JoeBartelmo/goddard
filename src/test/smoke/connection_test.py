#!/usr/bin/env python
#
# @file "connection_test.py"
# @authors "Joseph Bartelmo"
# @contact "joebartelmo@gmail.com"1
# @date "4/23/2016"
# @copyright "MIT"
#
import src.client


testClient = src.client.RTSPClient("129.21.143.53", 5900, None)

testClient.connect()
testClient.stream_synchronous()
testClient.disconnect()
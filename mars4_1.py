import serial
import os
import time
import re
import math
import threading
import numpy as np
import csv


class Mars(object):

	"""
DESCRIPTION
:Name:
	Mars

:Purpose:	
	this class was made for the purposes of controlling and operating the
	M.A.R.S.(Mechanized Autonomous Rail Scanner) built by RIT Hyperloop Team
	to scan & identify debris and damage in SpaceX's Hyperloop test track. This 
	python code talks with an Arduino over a Serial connection to operate the 
	robot. A four digit *Control Code*, typed in by a human operator, determines 
	exactly what the robot will do. 

:AUTHOR:
	Jeff Maggio
	last updated: May 31, 2016


:DISCLAIMER:
This source code is provided "as is" and without warranties as to performance 
or merchantability. The author and/or distributors of this source code may 
have made statements about this source code. Any such statements do not 
constitute warranties and shall not be relied on by the user in deciding 
whether to use this source code.

This source code is provided without any express or implied warranties 
whatsoever. Because of the diversity of conditions and hardware under which 
this source code may be used, no warranty of fitness for a particular purpose 
is offered. The user is advised to test the source code thoroughly before 
relying on it. The user must assume the entire risk of using the source code.


________________________________________________________________________________
	CONTROL CODE CONVENTION--> 'ABCD'
			-where 'A' is a binary operator to enable the robot
				(The robot must be enabled to move at all)
			-where 'B' is a binary operator that defines direction (fwd, rev)
			-where 'C' is a binary operator to engage the brake
			-where 'D' is a decimal integer (0-9) that defines the speed
				(Each integer roughly corresponds to that speed in MPH)

		eg. 1008 --> foward at 8mph
		eg. 1105 --> reverse at 5mph
		eg. 0010 --> motor disabled, brake engaged, full stop
		eg. 0103 --> motor not enabled, thus there will be no motion
________________________________________________________________________________
	
	In addition, this class contains functions to acquire all data sent from the
	arduino, process it and provide the operator with a variety of telemetry 
	information.

FUNCTIONS

	main()::  
		*********PRIMARY FUNCTION WHEN OPERATING M.A.R.S.***********		
		runs the initiatalization procedure
		sets up multiple threads to allow simultaneous DAQ, input and reactions
				utilizes:
					initialize()
					repeat_rps()
					repeat_input()
					connection_check()
				returns:
					NONE
	============================================================================
	initalize()::
		checks if arduino is properly connected, flushes Serial buffers and 
		starts the clock
				utilizes:
					NONE
				returns:
					NONE
	============================================================================
	repeat_rps()::
		continuously runs the rps() function
				utilizes:
					rps()
				returns:
					NONE
	============================================================================					
	repeat_input()::
		continuously runs the controller_input() function
				utilizes:
					controller_input()
				returns:
					NONE
	============================================================================
	connection_check()::
		continuously checks the connection with the controller's computer and 
		tells Mars to initiate autonomous mode if that connection is lost
				utilizes: 
					ping_control()
				returns:
					NONE
	============================================================================
	ping_control()::
		this function pings the controller's computer once and returns a 
		boolean value indictating whether connection is still good
				utilizes:
					NONE
				returns:
					connection status (boolean)					
	============================================================================
	daq():: 
		This function reads data from the arduino and then calculates a variety 
		of other values derived from it such as speed, power, batteryRemaining. 
				utilizes: 
					serial_readline()
					estimated_speed()
					estimated_power()
					distance_traveled()
					batteryRemaining()
				returns:
					telemetry array (list)					
	============================================================================
	make_pretty():: 
		this functions takes the dataArray from daq and returns a string with 
		all data formatted in a more human-readable manner 
				utilizes: 
					NONE
				returns:
					human-readable telemetry (string)					
	============================================================================
	serial_readline()::
		Reads the telemetry sent from the arduino
				utilizes:
					NONE
				returns:
					a single line of data sent from arduino (string)		
	============================================================================
	rps()::
		Reads, Prints and Saves the telemetry sent from the Arduino
		also displays a human-friendly format in the terminal for an operator
				utilizes:
					daq()
					make_pretty()
				returns:
					NONE		
	============================================================================
	controller_input()::
		checks if control code is valid and sends control code to the arduino
				utilizes:
					arduino_write()
					input_check()
				returns:
					NONE

	============================================================================
	arduino_write(controlCode)::
		writes the controlCode to the arduino over the Serial buffers
				utilizes:
					NONE
				returns:
					NONE					
	============================================================================
	input_check(userInput)::	
		checks the userInput to see if it follows Control Code Convention
				utilizes:
					NONE
				returns:
					whether or not user input qualifies (boolean)						
	============================================================================
	flush_buffers()::	
		flushes serial buffers
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	default_forward()::
		simply sends a control code to the arduino that will make MARS travel
		forward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	default_backward()::
		simply sends a control code to the arduino that will make MARS travel
		forward at 40percent speed
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	stop()::
		simply sends a control code to the arduino that will make MARS stop 
		unconditionally
				utilizes:
					NONE
				returns:
					NONE						
	============================================================================
	time_since_start()::
		returns the time since initalization began
				utilizes:
					NONE
				returns:
					time since initalization (float)						
	============================================================================
	estimated_speed()::
		estimates the current speed of MARS based off of RPM data
				utilizes:
					NONE
				returns:
					estimated speed in m/s (float)

	============================================================================
	estimated_power()::
		estimates the current power usage of mars based off of voltage and 
		current data
				utilizes:
					NONE
				returns:
					estimated power usage in Watts (float)	
	============================================================================
	battery_remaining(power *optional*, time *optional*)::
		if the user inputs power or time data, then this function will calculate
		how much energy remains in the batteries. otherwise ths will return the
		last calculated battery status
				utilizes:
					NONE
				returns:
					percentage of battery remaining (float)

--------------------------------------------------------------------------------

NEED TO ADD::
	autonomous() - sets up an autonomous mode
	led_brightness() - changes the brightness of the LEDS
	distance_traveled() - calculated distance traveled
	sensor_check() - continuously checks sensors, and returns a status code
	backup_comms() - turn on/off the LEDS to send emergency signals?
	motion_check() - is Mars still moving? ie. are we stuck?

	FIX DISTANCE TRAVELED AND BATTERY FUNCTIONS

	"""


	def __init__(self, controller_IP = "129.21.116.121",\
		arduino = None, tStart = None,initializeOkay = False,\
		 devicePath = '/dev/ttyACM3',baudRate = 9600, timeout = 5,\
		   shouldLog = True, logName = 'run1', isConnected = True,\
		    integrationTime = 0.0, tLastRead = 0, currentBattery = 192.0,\
		     totalBattery = 192.0, distanceTraveled = 0, currentSpeed = 0):
		self._controller_IP =  controller_IP #IP address of the control comp
		self._arduino = arduino #used in initialize(), NoneType now
		self._tStart = tStart #start time for logging purposes
		self._initializeOkay = initializeOkay #has initiatalization occured?
		self._devicePath = devicePath #location of control arduino on machine
		self._baudRate = baudRate #baud rate of serial connectiom, usually 9600
		self._timeout = timeout #time in sec to listen for telemetry b4 error
		self._shouldLog = shouldLog #boolean to deterime if telemetry is logged
		self._logName = logName #name of the log
		self._isConnected = isConnected #have we lost connection with control?
		self._integrationTime = integrationTime #time since last recieving data
		self._tLastRead = tLastRead #time data was last read
		self._currentBattery = currentBattery #current updated battery remaining
		self._totalBattery = totalBattery#original battery size
		self._distanceTraveled =  distanceTraveled # distance traveled so far
		self._currentSpeed = currentSpeed

	def main(self):
		#run initalize function
		## program should quit if arduino isn't connected
		self.initalize()
	#### SETTING UP MULTIPLE THREADS HERE ####
		dataThread = threading.Thread(target = self.repeat_rps)
		inputThread =  threading.Thread(target = self.repeat_input)
		pingingThread = threading.Thread(target = self.connection_check)

		try:
			dataThread.start() #rps() thread
			inputThread.start() #repeat_input() thread
			# pingingThread.start() #connection_check() thread
		except Exception as e:
			print "error starting Multithreading ({})".format(e)
			print "program will terminate"
			raise SystemExit



	def initalize(self):
		print "initializing setup"
		print "checking if arduino is connected..."
		#check if arduino is connected on device path
		## exit program if connection failure
		try:
			# SELF._ARDUINO TYPE CHANGE: None-->Serial Object
			self._arduino = serial.Serial(self._devicePath,self._baudRate)
		except serial.serialutil.SerialException:
			print "arduino not connected or device path wrong" 
			print "program will terminate"
			raise SystemExit

		print "arduino connected"

		#naming the log
		if self._shouldLog == True:
			self._logName = raw_input("please input the name for the datalog: ")

		print"flushing serial buffers..."	
		self._arduino.flushInput() #flushing the serial input buffer
		self._arduino.flushOutput() #flushing the serial output buffer

		print "Initialization complete"
		self._initializeOkay = True
		self._tStart = time.time()

		print "Starting..."	
		print ""


	def repeat_rps(self):
		while self._isConnected == True:
			self.rps()

	def repeat_input(self):
		while self._isConnected == True:
			self.controller_input()

	def connection_check(self):
		ipToCheck = self._controller_IP
		while True:
			time.sleep(5)
			connectionStatus = self.ping_control(ipToCheck)
			if connectionStatus == False:
				self._isConnected = False
				self.autonomous(engage = True) #if connection is lost, then enter autonomous mode
				print "engaging autopilot"
			else: 
				self.autonomous(engage = False)
				print "user reconnected, autopilot disengaged"


	def ping_control(self, ipToCheck):
		"""
		this function pings the controlling computer and returns a boolean
		indicating whether or not we are still connected

		"""
		str(ipToCheck)
		print type(os.system("ping -c 1 -w2 -t 3" + ipToCheck + " > ip_log.txt"))
		response = os.system("ping -c 1 -w2 -t 3" + ipToCheck +  " > ip_log.txt")
		# and then check the response...
		print response
		if response == "0":
			return True
		else:
			return False


	def daq(self):
		if self._initializeOkay == False:
			self.initalize()

		rawInput = self.serial_readline() #reading Serialdata

		rawArray = re.split(',',rawInput)
		
		#independent data (raw from arduino)
		rpm = rawArray[0]
		sysV = rawArray[1]
		sysI = rawArray[2]



		#first set dependent (calculated based off of raw data)
		speed = self.estimated_speed(rpm) #speed in m/s
		power = self.estimated_power(sysV, sysI) #power in Watts

		#second set dependent (calculated based off of above set)
		distance, distanceTraveled = self.distance_traveled(speed) #in Meters
		batteryRemaining = self.battery_remaining(power)

		#TX1-side data
		integrationTime = self._integrationTime
		runClock = self.time_since_start()
		isConnected = self._isConnected

		#compiling all data for later integration
		telemetryArray = [runClock,distanceTraveled,speed,power,\
		batteryRemaining,integrationTime,isConnected, rpm, sysV, sysI]

		return telemetryArray


	def make_pretty(self, dataArray):
		"""this function converts the DAQ output to a more convienent format for
		a human operator"""
			########### NEED TO SET UP A DATATYPE CHECK ##########
		runClock = dataArray[0]
		distance = dataArray[1]
		speed = dataArray[2]
		power = dataArray[3]
		battery = dataArray[4]
		integTime = dataArray[5]
		connectionStatus = dataArray[6]
		motorRpm = dataArray[7]
		systemVoltage = dataArray[8]
		systemCurrent = dataArray[9]

		minutes,seconds = divmod(runClock, 60)

		minSecString = str(int(minutes)) + ":" + str(int(seconds)) + "{  "
		distanceString = str(distance)+"meters, "
		speedString = str(speed) + "m/s, "
		powerString = str(power) + "Watts, "
		batteryString = str(battery) + "%, "
		#integration time isn't needed for operator
		if connectionStatus == True:
			connectionString = "Connected"
		else:
			connectionString = "Disconnected"

		rpmString = str(motorRpm) + "rpm, "
		voltageString = str(systemVoltage) + "V, "
		currentString = str(systemCurrent) + "A, "

		operatorString = minSecString + distanceString + speedString + \
		powerString + batteryString + rpmString + voltageString + \
		currentString +connectionString

		return operatorString



	def serial_readline(self):
		#only attempt to read if initialization has occured
		if self._initializeOkay == False: 
			self.initalize()

		#begining a waiting clock for timeout
		waitStart = time.time()
		waitTime = time.time() - waitStart
		timeout = self._timeout

#______________________Pulling Data from Arduino_______________________________#
		#only readline if there is data in the buffer 
		## continue checking buffer only if waiting time is less than timeout
		while self._arduino.inWaiting() == 0:
			if waitTime < timeout:
				waitTime =  time.time() - waitStart
			elif waitTime >= timeout:
				print "no data coming from arduino before connection timeout"
				print "ending program, check arduino code or timeout duration"
				print "attempting re-initialization..."
				self.initialize()
		else:
			time.sleep(.001) #added short delay just in case data was in transit
			serialData = self._arduino.readline()#read telemetry sent by Arduino
			self._arduino.flushInput() #flushing in case there was a buildup
#______________________________________________________________________________#
			#finding integration time
			##resetting the time since last read
			self._integrationTime = self.time_since_start() - self._tLastRead
			self._tLastRead = self.time_since_start() 

			return serialData



	def rps(self): #rps: Read, Print and Save
		daqData = self.daq()
		operatorString = self.make_pretty(daqData)

		# print operatorString #print to console so operator can interpret

		#saving to file for logging purposes
		if self._shouldLog == True:
		#operator File = console log, easier for a human to interpret
			operatorFileName = self._logName + '_operator_log.txt'
			operatorFile = open(operatorFileName,'a')
			operatorFile.write(operatorString) 
			operatorFile.close()
		
		#raw File - raw DAQ log, easier for a machine to process
			rawFileName =  self._logName + '_machine_log.csv'
			with open(rawFileName, 'a') as rawFile:
				rawWriter = csv.writer(rawFile)
				rawWriter.writerow(daqData)
			
		## There are automatically 2 logs saved
		### One formatted in a more human-friendly way
		#### and another in a machine-readable '.csv'



	def controller_input(self):
		#ask for control code input from user
		controlCode = raw_input("4 digit control code: ")

		#check if control code is within parameters
		codeOkay = self.input_check(controlCode)
		if codeOkay == True:
			self.arduino_write(controlCode)
			print controlCode
		else: 
			print "control code must be a 4 digit code"
			print "with the first 3 digits being binary, the last is decimal"
			self.controller_input()



	def arduino_write(self, controlCode):
		#only send code if initialization has occured
		if self._initializeOkay == False:
			self.initalize()

		self._arduino.write(controlCode) #send control code to arduino



	def input_check(self, userInput):
		"""
		This function checks the controlCode input and checks if it is within
		the convention described above in the docstring.

		This function could probably be remade in a more straightforward manner
		"""

		#checking the overall length of string. length must = 4
		if len(userInput) == 4:
			lengthOkay = True
		else: 
			lengthOkay = False
			print "Control Code must have exactly 4 digits"

		enableInput = userInput[0]
		directionInput = userInput[1]
		brakeInput = userInput[2]
		speedInput = userInput[3]


#_______________CHECKING TO SEE IF EACH INPUT MEETS CRITERIA _________________#
		#CHECKING IF ENABLE INPUT IS BINARY
		if enableInput == "0" or enableInput == "1":
			enableOkay = True
		else:
			enableOkay = False
			print "enable digit must be binary"

		#CHECKING IF DIRECTION INPUT IS BINARY
		if directionInput == "0" or directionInput == "1":
			directionOkay = True
		else:
			directionOkay = False
			print "direction digit must be binary"
			
		#CHECKING IF BRAKE INPUT IS BINARY
		if brakeInput == "0" or brakeInput == "1":
			brakeOkay = True
		else:
			brakeOkay = False
			print "direction digit must be binary"


		#CHECKING TO SEE IF SPEED INPUT IS DECIMAL (0-9)
		if speedInput.isdigit() == True: #check to see if input is a digit
			speedOkay = True
		else:
			speedOkay = False


	############## Returning True/False based on previous tests ##############
		if enableOkay == True and directionOkay == True and brakeOkay == True\
		and speedOkay == True:
			return True #return True if all inputs meet criteria
		else:
			return False #return False if otherwise


	def flush_buffers():
		"""this function just flushes the Serial buffers"""
		#only attempt to flush if initialization has occured
		if self._initializeOkay == False: 
			self.initalize()

		print"flushing serial buffers..."	
		self._arduino.flushInput() #flushing the serial input buffer
		self._arduino.flushOutput() #flushing the serial output buffer


	def default_forward(self):
		"""
		This function just sends the control code associated with moving forward
		at 40percent speed. This will be the function that autonomous mode will
		call
		"""
		defaultForwardCode = "1004"
		arduino_write(defaultForwardCode)



	def default_backward(self):
		"""
		This function just sends the control code associated with moving 
		backward at 40percent speed. This will be a function that autonomous
		mode will call
		"""

		defaultBackwardCode = "1104"
		self.arduino_write(defaultBackwardCode)


	def stop(self):
		"""
		This function sends a full stop command to the arduino to stop the Mars
		"""

		fullStopCode = "0010"
		self.arduino_write(fullStopCode)


	def time_since_start(self):
		currentTime = time.time()

		tSinceStart = currentTime - self._tStart
		return tSinceStart


	def estimated_speed(self, rpm):
		"""
		This function guesses how fast Mars is going based on the lastest RPM
		data from the DAQ. 

		It does not take into account any other factors or forces, as a result
		this is an ESTIMATED SPEED, not a real speed

		this conversion is will only work for the current generation of MARS and
		is a function of this equation

			speed in mph ~= rpm/221
			speed in m/s ~= (rpm/221)*0.44704
		"""
		rpm = float(rpm) #rpm must be a float
		estMph = rpm/221.0 #SPEED IN MPH - Not sure if this will be used
		estMps = (rpm/221.0)*0.44704 #SPEED in M/S

		returnEstMps = round(estMps, 1)
		self._currentSpeed = returnEstMps
		return returnEstMps

	def estimated_power(self, sysVoltage, sysCurrent):
		"""
		This function estimates the power draw of mars based off of the system
		voltage and current which is collected from the arduino's ammeter

		P = V*I
		"""
		sysVoltage = float(sysVoltage)
		sysCurrent = float(sysCurrent)
		estPower = sysVoltage * sysCurrent

		returnPower = round(estPower, 2)
		return returnPower



	def battery_remaining(self,power=0.0, time = None):
		if time == None:
			time = self._integrationTime 
	########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########
		"""
		if the user decides to input a power, then this function will 
		calculate how much battery power remains given the current
		integrationTime and returns the new battery percentage

		Otherwise this function simply returns the last calculated battery
		capacity

		"""
		if power != 0.0:
			joulesUsed  = float(power) * time
			whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours

			self._currentBattery = self._currentBattery - whrUsed
			#subtracting energy used from battery total

		battPercent = self._currentBattery/self._totalBattery * 100.0
		returnBattPercent = round(battPercent, 1)
		return returnBattPercent

	def distance_traveled(self, speed, time=None):
		if time == None:
			time = self._integrationTime

		intervalDistance = speed * time
		self._distanceTraveled = self._distanceTraveled + intervalDistance
		totalDistance = self._distanceTraveled
		
		returnIntervalDistance = round(intervalDistance,1)
		returnTotalDistance = round(totalDistance, 1)

		return returnIntervalDistance,returnTotalDistance


	def autonomous(self, engage = True):
		if self._currentSpeed > 0.0:
			self.default_forward()
		elif self._currentSpeed < 0.0:
			self.default_backward()
		else:
			self.stop()



if __name__ == "__main__":
	m = Mars(controller_IP = "www.google.com")
	m.main()
	# m.arduino_write('0010')
















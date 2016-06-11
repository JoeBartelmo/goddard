import serial #used to communicate with the arduino over a serial bus
import os 
import time #used for the runclock and real time integrators
import re #used primarily to split DAQ strings and generate an array of data
import math #for math
import csv #used to generate a machine log
import pyping #used to ping master controller


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
	robot. A multicharacter *Control Code*, typed in by a human operator, 
	determines exactly what MARS will do. 

	In addition, this class contains functions to acquire all data sent from the
	arduino, process it and provide the operator with a variety of telemetry 
	information.


:AUTHOR:
	Jeff Maggio
	RIT Hyperloop Imaging Team
	http://hyperloop.rit.edu/team.html

:CONTACT:
	Feel free to contact this author at any point in time
	email: jxm9264@rit.edu | jmaggio14@gmail.com
	phone: 1-513-550-9231

:UPDATED:
	last updated: June 3, 2016

	

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
					-----------------------------------------
					|        CONTROL CODE CONVENTION        |
					-----------------------------------------
		Control codes are broken up into two formats, with each format
		controlling a different aspect of MARS. These formats are distinquished
		by an identifer placed at the beginning of the control code.

	# MOTION CONTROL
		-Placing an 'M' at the beginning of a 4 digit control code indicates 
		that the user wants to control the motion of MARS

		$FORMAT = "MABCD"

		where:
			'M' is the identifer "M"
			'A' is a binary operator to enable the Motor
					'-->(The motor must be enabled to move at all)
			'B' is a binary operator that defines direction (fwd, rev)
			'C' is a binary operator to engage the brake
			'D' is a decimal integer (0-9) that defines the speed
					'-->(Each integer roughly corresponds 1Mph or .5m/s)

			Examples
				"M1008" --> foward at 8mph
				"M1105" --> reverse at 5mph
				"M0010" --> motor disabled, brake engaged (unconditional stop)
				"J1108" --> Unknown identifier 'J', code is not processed

	# LED CONTROL
		-Placing an 'L' at the beginning of a 2 character control code indicates
		that the user wants to define the luminance of MARS' LEDS

		$FORMAT = "LX"

		where:
			'L' is the identifier "L"
			'X' is a decimal integer (0-9) that defines the brightness on a
			linear scale.

			Examples
				"L0" --> LEDs off
				"L3" --> LEDs on 30percent strength
				"L9" --> LEDs on full strength
				"Q9" --> Unknown identifier 'Q', code is not processed
________________________________________________________________________________	

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
		starts the runClock
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
		backward at 40percent speed
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


	def __init__(self, masterIP, devicePath, baudRate, timeout,\
		isLogging, logName, trackLength, configFile, enableRecall,\
		recallPercent, arduino = None, initializeOkay = None, tStart = None,\
		 currentBattery = None,	totalBattery = None, distanceTraveled = 0,\
		  currentSpeed = 0,isConnected=None,):
		self._masterIP =  masterIP #IP address of the control comp
		self._arduino = arduino #used in initialize(), NoneType for now
		self._initializeOkay = initializeOkay #has initiatalization occured?
		self._devicePath = devicePath #location of control arduino on machine
		self._baudRate = baudRate #baud rate of serial connectiom, usually 9600
		self._timeout = timeout #time in sec to listen for telemetry b4 error
		self._isLogging = isLogging #boolean to deterime if telemetry is logged
		self._logName = logName #name of the log
		self._isConnected = isConnected #have we lost connection with control?
		self._currentBattery = currentBattery #current updated battery remaining
		self._totalBattery = totalBattery#original battery size
		self._distanceTraveled =  distanceTraveled # distance traveled so far
		self._currentSpeed = currentSpeed # last recorded speed of MARS
		self._configFile = configFile #name of the settings file
		self._recallPercent = recallPercent #point at which Mars automatically
											##recalls itself
		self._trackLength = trackLength #length of the track, used for recall
		self._enableRecall = enableRecall


	
	def initalize(self):
		print ""
		print "beginning initialization..."

		# print "loading configs from {}".format(self._configFile)
		# self.load_configs() #loading the configurations from settings

		print "checking if arduino is connected..."
		#check if arduino is connected on device path
		## exit program if connection failure
		try:
		# SELF._ARDUINO TYPE CHANGE: None-->Serial Object
			self._arduino = serial.Serial(self._devicePath,self._baudRate)

		except serial.serialutil.SerialException:
			print "arduino not connected or device path wrong" 
			print "check MARS user manual for details" 
			print "unable to continue, program will now terminate"
			raise SystemExit

		print "arduino connected"


		print"flushing serial buffers..."	
		self._arduino.flushInput() #flushing the serial input buffer
		self._arduino.flushOutput() #flushing the serial output buffer

		print "Initialization complete"
		self._initializeOkay = True
		#BEGINNING RUN CLOCK --> tStart used to calculate runclock
		global tStart
		tStart = time.time()
		global integrationTime
		integrationTime = 0.0

		time.sleep(1)
		global tLastRead
		tLastRead = self.time_since_start()
		print ""

		

	def repeat_rps(self):
		while True:
			self.rps()

	def repeat_input(self):
		while True:
			self.controller_input()

	def connection_check(self):
		ipToCheck = self._masterIP
		while True:
			time.sleep(5)
			connectionStatus = self.ping_control(ipToCheck)
			if connectionStatus == False:
				self._isConnected = False
				self.autonomous(engage = True) #if connection is lost, then enter autonomous mode
				print "engaging autopilot"
			else: 
				self.autonomous(engage = False)


	def ping_control(self, ipToCheck):
		"""
		this function pings the controlling computer and returns a boolean
		indicating whether or not we are still connected

		"""
		r = pyping.ping(self._masterIP)

		if r.ret_code == 0: 
			#master is still reachable
			return True
		else:
			#master is not reachable, connection is lost
		    return False


	def daq(self):
		if self._initializeOkay == False:
			self.initalize()

		try:
			rawInput = self.serial_readline() #reading Serialdata
			print rawInput

			rawArray = re.split(',',rawInput)
			#independent data (raw from arduino)
			rpm = rawArray[0]
			sysV = rawArray[1]
			sysI = rawArray[2]
			sysI = sysI[0:4]
			#first set dependent (calculated based off of raw data)
			speed = self.estimated_speed(rpm) #speed in m/s
			power = self.estimated_power(sysV, sysI) #power in Watts

			#second set dependent (calculated based off of above set)
			distance, distanceTraveled = self.distance_traveled(speed) #in Meters
			batteryRemaining = self.battery_remaining(power)

			#TX1-side data
			global integrationTime
			integrationTime2 = round(integrationTime, 4)
			runClock = round(self.time_since_start(), 4)
			isConnected = self._isConnected


			#compiling all data for later integration
			telemetryArray = [runClock,distanceTraveled,speed,power,\
			batteryRemaining,integrationTime2,isConnected, rpm, sysV, sysI]

			# print telemetryArray
		except Exception as e:
			print "unable to acquire data due to {}".format(e)
			print "attemting to correct"
			self.daq() 

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
			global integrationTime
			global tLastRead

			integrationTime = self.time_since_start() - tLastRead
			tLastRead = self.time_since_start() 

			return serialData



	def rps(self): #rps: Read, Print and Save
		daqData = self.daq()
		operatorString = self.make_pretty(daqData)

		# print operatorString #print to console so operator can interpret
		# print ""
		#saving to file for logging purposes
		if self._isLogging == True:
		#operator File = console log, easier for a human to interpret
			operatorFileName = 'logs/'+ self._logName + '_operator_log.txt'
			operatorFile = open(operatorFileName,'a')
			operatorFile.write(operatorString+'\r\n') 
			operatorFile.close()
		
		#raw File - raw DAQ log, easier for a machine to process
			rawFileName =  'logs/'+ self._logName + '_machine_log.csv'
			with open(rawFileName, 'a') as rawFile:
				rawWriter = csv.writer(rawFile)
				rawWriter.writerow(daqData)
		
		## There are automatically 2 logs saved
		### One formatted in a more human-friendly way
		#### and another in a machine-readable '.csv'



	def controller_input(self):
		#ask for control code input from user
		controlCode = raw_input("LED or motion control code: ")
		#check if control code is within parameters
		codeOkay = self.input_check(controlCode)

		if codeOkay == True:
			self.arduino_write(controlCode) #write code to arduino
			print controlCode #print control code for reference
		else: 
			print "control code must follow strict convention"
			print "check MARS user manual for specifics"

	def arduino_write(self, controlCode):
		#only send code if initialization has occured
		if self._initializeOkay == False:
			self.initalize()

		self._arduino.write(controlCode) #send control code to arduino



	def input_check(self, userInput):
		"""
		This function checks the controlCode input and checks if it is within
		the convention described above at the begining of the primary docstring.

		It uses a complex series of nested if-statements to check the code.

		This function could probably be remade in a more straightforward manner,
		an option might be to use dictionaries or nested lambda functions 
				'--> ie. the python equivalent of a switch statement.

		possible alternatives:
					https://code.activestate.com/recipes/410692/

		"""

		codeIdentifier = userInput[0]
		codeIdentifier = codeIdentifier.upper()

		#____TESTING IF THE IDENTIFER IS WITHIN PARAMETERS____#

	#---------------BEGIN LED CODE CHECK----------------------#
		if codeIdentifier == "L":
			#____testing the length of the input____#	
			if len(userInput) == 2:
				lengthOkay = True
			else:
				lengthOkay = False

			#===testing if the second value is a digit===#
			if userInput[1].isdigit() == True:
				valuesOkay = True
			else:
				valuesOkay = False
			

			#____Compiling the output____#	
			if lengthOkay == True and valuesOkay == True:
				testResult = True
			else:
				testResult = False
				

	#---------------BEGIN MOTOR CODE CHECK----------------------#
		elif codeIdentifier == "M":
		#____testing the length of the input____#	
			if len(userInput) == 5:
				lengthOkay = True
			else:
				return False #--> return false is the input isn't right length
		#____checking if the enable value is binary____#
			if userInput[1] == "0" or userInput[1] == "1":
				enableOkay = True
			else:
				enableOkay =  False
		#____checking if the reverse value is binary____#
			if userInput[2] == "0" or userInput[2] == "1":
				reverseOkay = True
			else:
				reverseOkay =  False
		#____checking if the brake value is binary____#
			if userInput[3] == "0" or userInput[3] == "1":
				brakeOkay = True
			else:
				brakeOkay =  False
		#____checking if the speed value is decimal____#
			speedValue = userInput[4]
			if speedValue.isdigit() == True:
				speedOkay = True
			else:
				speedOkay = False

			a = lengthOkay
			b = enableOkay
			c = reverseOkay
			d = brakeOkay
			e = speedOkay

			if a==True and b==True and c==True and d==True and e==True:
				testResult = True
			else:
				testResult = False

		else:
			print "control code must have an identifier"
			print "------------------------------------"
			print "check MARS user manual for specifics"
			print "------------------------------------"			
			testResult = False
#######DEBUGGING CODE ####################
		if testResult == True:
			print "test is positive"
		elif testResult == False:
			print "test is negative"


		return testResult
		# return True
		

	def flush_buffers(self):
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
		defaultForwardCode = "M1104"
		self.arduino_write(defaultForwardCode)



	def default_backward(self):
		"""
		This function just sends the control code associated with moving 
		backward at 40percent speed. This will be a function that autonomous
		mode will call
		"""

		defaultBackwardCode = "M1004"
		self.arduino_write(defaultBackwardCode)


	def stop(self):
		"""
		This function sends a full stop command to the arduino to stop the Mars
		"""

		fullStopCode = "M0010"
		self.arduino_write(fullStopCode)


	def time_since_start(self):
		global tStart
		currentTime = time.time()

		tSinceStart = currentTime - tStart
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
		estMps = (rpm/221.0)*0.44704 #estimated SPEED in M/S

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

		powerReturned = round(estPower, 2)
		return powerReturned



	def battery_remaining(self,power=None, time = None):
		if time == None:
			time = integrationTime 
	########^^^^^^^^FIX THIS ONCE DEBUGGING IS COMPLETE^^^^^^^^###########
		"""
		if the user decides to input a power, then this function will 
		calculate how much battery power remains given the current
		integrationTime and returns the new battery percentage

		Otherwise this function simply returns the last calculated battery
		capacity

		"""
		if power != None:
			joulesUsed  = float(power) * time
			whrUsed = joulesUsed/3600.0 #converting Joules to Watt*hours

			self._currentBattery = self._currentBattery - whrUsed
			#subtracting energy used from battery total

		battPercent = self._currentBattery/self._totalBattery * 100.0
		battPercentReturned = round(battPercent, 1)

		return battPercentReturned

	def distance_traveled(self, speed, time=None):
		if time == None:
			time = integrationTime

		intervalDistance = speed * time
		self._distanceTraveled = self._distanceTraveled + intervalDistance
		totalDistance = self._distanceTraveled
		
		intervalDistanceReturned = round(intervalDistance,1)
		totalDistanceReturned = round(totalDistance, 1)

		return intervalDistanceReturned,totalDistanceReturned


	# def autonomous_action(self, engage = True):
	# 	batteryRemaining = self.batteryRemaining
	# 	if engage == True:
	# 		if batteryRemaining + 5.0 >= self._recallPercent:


	# 		#checking battery percentage. Is automatic Recall needed? 







# if __name__ == "__main__":
# 	m = Mars()
# 	try:
# 		m.main()
# 	except KeyboardInterrupt:
# 		m.stop()















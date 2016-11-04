/**
* Copyright (c) 2016, Jeffrey Maggio and Joseph Bartelmo
* 
* Permission is hereby granted, free of charge, to any person obtaining a copy of this software and
* associated documentation files (the "Software"), to deal in the Software without restriction,
* including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so,
* subject to the following conditions:
* 
* The above copyright notice and this permission notice shall be included in all copies or substantial 
* portions of the Software.
* 
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT
* LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
* IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
* WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
*/
#include "MemoryFree.h"
#include "DaqTelemetry.h"

//Telemetry
DaqTelemetry *daqTelemetry;

//Timing
unsigned long lastTime = 0;
unsigned long clockCorrection = 64;
int clockCorrectionInt = 64;

//Motor
int enablePin = 13; //enable/disable motor
int revPin = 11; //seting fwd/rev
int brakePin = 12; //brake pin
int speedPin = 5; //speedPin
int encoderPin = A5; //pin for motor controller
int referencePin = A4; //reference Pin to compare against current, voltage and encoder pin
boolean directionOfTravel;
double rpmOffset = -30;

//LEDS
int ledPin = 9;

//Ammeter
int voltagePin = A0; //ammeter voltage pin
int currentPin = A4; //ammeter current pin
double currentOffset = 1.0;

//IRdistance sensors
int frontIrPin = A2;
int backIrPin = A3;
int numSamples = 10;
int irDelayTime = clockCorrectionInt * 60;

//Conversions
double rpmMultiplier = 800;
double voltageMultiplier = 0.076982;
double currentMultiplier = .135;
double currentDivisor = 7.4;
double scaleOffset = 512;
double maxRpm = 1200;
double minRpm = -1200;

//Voltage Reference
bool useRef = false;
int realReference = 512;

//Watchdog
bool watchdogEnabled = false;
unsigned long watchdogTimer;
unsigned long recallTime = 30000;
unsigned long shutdownTime = 1200000;
String recallCode = "M1005";

//Logging
String logs = "marsduino initated";

//Memcheck Mode
bool memCheck = false;




void setup() {
  //modifies registries to increase PWM frequency
  TCCR1B = (TCCR1B & 0b11111000) | 0x01;
  TCCR0B = (TCCR0B & 0b11111000) | 0x01;

  //enabling pins & setting status to LOW

  //Motor Control
  pinMode(enablePin, OUTPUT);
  pinMode(revPin, OUTPUT);
  pinMode(brakePin, OUTPUT);
  pinMode(speedPin, OUTPUT);
  digitalWrite(enablePin, LOW);
  digitalWrite(revPin, LOW);
  digitalWrite(brakePin, LOW);
  analogWrite(speedPin, LOW);

  //LEDS
  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);


  //enabling the serial connection
  Serial.begin(9600);
}

/**
   Quick conversion that relies on the offset of the character '0'
   @param c: character to be encoded
*/


/**
   Computes the distance from "WALL-E" (a distance sensor)
   @param irPin: The pin at which to access the distance sensor
*/
double ir_distance(int irPin, int voltageOffset)
{
  int sampleSum = 0;

  for (int index = 0; index < numSamples; index++)
  {
    int distanceVoltage = analogRead(irPin) + voltageOffset;
    sampleSum += distanceVoltage;
    delay(irDelayTime);
  }

  // average divided by numSamples to average, then divided by 205 to convert to voltage
  double avgVoltage = ((double) sampleSum / (double) numSamples) / 205.0;
  double distance = -1;
  if (avgVoltage > 2.5) {
    distance = 0;
  }
  else if (avgVoltage < 1.4) {
    distance = -1;
  }
  else {
    // These coefficents are not subject to change, and have no offical name
    // To obtain these values we regressed using a table of Distance vs Voltage
    distance = (double)(1011.6 * .01 * pow(avgVoltage, -2.621));
  }
  return distance;
}

/**
   Reads a string from serial input and parses based off of our format
   specified in our documentation, then executes given command.
*/



int charToInt(char c) {
  return int(c - '0');
}

String retrieve_code(){
  String input = Serial.readString();
  return input;
}

void process_code(String input){
  /*
   * Processes Input Control codes
   */
   
  char codeArray[8]; //input string turned into an array
  input.toCharArray(codeArray, 6);

  //First character defines what type of command
  char first = codeArray[0];

  switch (first) {
    //Motor code
    case 'M': { /*Motor codes*/ 
        char enable = codeArray[1] == '0' ? LOW : HIGH;
        char reverse = codeArray[2] == '0' ? LOW : HIGH;
        char brake = codeArray[3] == '0' ? LOW : HIGH;
        char speedValue = codeArray[4];

        digitalWrite(enablePin, enable); //ENABLE PIN(13)
        digitalWrite(revPin, reverse); //REVERSE PIN(7)
        digitalWrite(brakePin, brake); //NOTE BRAKE IS AN ACTIVE HIGH BRAKE PIN(12)

        //SPEED PIN(5)
        int speedDutyCycle = int(charToInt(speedValue) * 25.5); //converts input A0 a 0-255 scale
        analogWrite(speedPin, speedDutyCycle); //sets up PWM on the speedPin

        //Changing the global direction for reference in the DAQ
        directionOfTravel = reverse; // one is forwards, zero is backwards
        logs = "motor code set to level to " + input.substring(1);
        break;
      }

    case 'L': { /*LED codes*/
        char ledValue = codeArray[1];
        int ledDutyCycle = int(charToInt(ledValue) * 25.5);
        analogWrite(ledPin, ledDutyCycle); //sets up PWM on the speedPin
        logs = "LEDs set to level to " + String(ledValue);
        break;
      }
    case 'D': {
//      useRef = true;
      realReference = input.substring(1).toInt();
      logs = "Voltage Reference set to " + input.substring(1);
      break;
    }
    case 'S': {
      useRef = false;
      logs = "Voltage Reference disabled";
      break;
    }
    case 'R': {/*setting RPM multiplier*/
      String inputRpm = input.substring(1);
      rpmMultiplier = inputRpm.toDouble();
      logs = "RPM multiplier set to " + String(rpmMultiplier);
      break;
    }
    case 'V': {/*setting Voltage Multiplier*/
      String inputVoltage = input.substring(1);
      voltageMultiplier = inputVoltage.toDouble();
      logs = "Voltage Multiplier set to " + String(voltageMultiplier);
      break;
    }
    case 'I': { /* setting Current Multiplier */
      String inputCurrent = input.substring(1);
      currentMultiplier = inputCurrent.toDouble();
      logs = "Current Multiplier set to " + String(currentMultiplier);
      break;
    }
    case 'W': {/*watchdog timer reset*/
      watchdogEnabled = true;
      watchdogTimer = 0;
      logs = "Watchdog Timer Reset";
      break;
    }
    case 'Q': {/*watchdog timer disabled*/
      watchdogEnabled = false;
      logs = "Watchdog Timer Disabled";
      break;
    }
    case 'C': { /*memory mode enabled*/
      memCheck = true;
      logs = "Memory Check enabled";
      break;
    }
    case 'X':{ /*memory mode disabled*/
      memCheck = false;
      logs = "Memory Check disabled";
      break;
    }
  }
}


DaqTelemetry* daq()
  /*
   * acquires values from sensors via input pins and dervies the values in standard units 
   * 
   */

{
  daqTelemetry = new DaqTelemetry();
  int voltageOffset;
  if(useRef == true){
    //generating an offset based off of the reference voltage sent from motor controller
    double referenceVoltage = analogRead(referencePin);
    voltageOffset = int(referenceVoltage-realReference);
  }  
  else{
    voltageOffset = 0;
  }
  
  //Motor Calculations
  double encoderVoltage = ( analogRead(encoderPin) + voltageOffset ); //.0049 convert to real voltage values
  double scaledVoltage = (encoderVoltage - scaleOffset) * .0049;
  double finalRpm = scaledVoltage * rpmMultiplier + rpmOffset;

  if((scaledVoltage < -1.5) && (scaledVoltage > -2.0)){  
    finalRpm = minRpm;  }
  else if (scaledVoltage < -2.0){
    finalRpm = 0.0; }
  else if (scaledVoltage > 1.5){
    finalRpm = maxRpm;  }
  
  if(abs(finalRpm) < (maxRpm / 10.0) ){
    finalRpm = 0.0;
  }
    
  //System Voltage Calculations
  double inputV = analogRead(voltagePin) + voltageOffset;
  double finalV = (double)inputV * (double)voltageMultiplier;
  
  //System Current Calculations
  double inputI = (double)analogRead(currentPin) + (double)voltageOffset;
  double finalI =  (double)inputI * (double)currentMultiplier;
//  Serial.println(finalI);
  if(finalI < 5.0){
    finalI = 5.0;
  }
    

  //Distance Calculations
  double distance;
  if(directionOfTravel == 1){
    distance = ir_distance(backIrPin, voltageOffset);  
  }
  else {
    distance = ir_distance(frontIrPin, voltageOffset);  
  }
  


 //assigning values to daqTelemetry object  
  daqTelemetry->systemRpm = finalRpm;
  daqTelemetry->systemVoltage = finalV; 
  daqTelemetry->systemCurrent = finalI;
  daqTelemetry->distance = distance;

  return daqTelemetry;
}

String distance_to_string(double distance){
  /*
   * converts doubles to a string type
   */
  
  String outputDistance = (String)distance;
    
  if(outputDistance == "-1") {
     outputDistance = "out of range";
  }
  return outputDistance;
}


void save_and_send(DaqTelemetry *daqTelemetry)
  /*
   * compiles all the daqTelemetry, logs and runclock and forwards it along
   * to the controlling computer
   * 
   */
{
  String outputDistance = distance_to_string(daqTelemetry->distance);
  
  String daqString = String(daqTelemetry->systemRpm) + "," +
                     String(daqTelemetry->systemVoltage) + "," +
                     String(daqTelemetry->systemCurrent) + "," +
                     String(outputDistance) + "," +
                     logs + "," +
                     ( (millis() / clockCorrection) / 1000.0 );
  Serial.println(daqString);
}

unsigned long update_watchdog_timer(){
  /*
   * updates the watchdog timer 
   */
  watchdogTimer = watchdogTimer + ( ( millis() / clockCorrection ) - lastTime );
  lastTime = millis() / clockCorrection;
  return watchdogTimer;
}

void memory_check(){
  /*
   * This function just prints out the current amount of free memory possessed by the arduino
   * used only in troubleshooting scenarios
   * 
   * running this method with Goddard will effectively break the MARS controller
   */
  
  Serial.print("freeMemory()=");
  Serial.println(freeMemory()); 
}


void emergency_shutdown(){
  /*
   * This function shuts down the watchdog and turns all pins off (to effectively disengage the motor)
   * 
   * only used in the event that that the arduino has recieved no contact from MARS
   * for a long duration. the arduino assumes that something catastrophic has happened 
   * and MARS is stuck in the tube without any controlling software.
   * 
   */
  watchdogEnabled = false;
  memCheck = false;
  digitalWrite(enablePin, LOW);
  digitalWrite(revPin, LOW);
  digitalWrite(brakePin, LOW);
  digitalWrite(speedPin,LOW);
  digitalWrite(ledPin,LOW);
}

void loop() {
 if (Serial.available() > 0) {
    process_code( retrieve_code() );
 }
 daqTelemetry = daq();
 save_and_send(daqTelemetry);
  
 update_watchdog_timer();
  if(watchdogEnabled == true){
    if(watchdogTimer > recallTime){
      process_code( recallCode );
    }
    else if(watchdogTimer > shutdownTime){
      emergency_shutdown();
    }
  }
  if(memCheck == true){
    memory_check();
  }
  logs = "Null";
  delete daqTelemetry;
}

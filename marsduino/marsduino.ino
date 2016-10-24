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

//Motor
int enablePin = 13; //enable/disable motor
int revPin = 11; //seting fwd/rev
int brakePin = 12; //brake pin
int speedPin = 5; //speedPin
int voltagePin = A0; //ammeter voltage pin
int currentPin = A1; //ammeter current pin
int encoderPin = A5; //pin for motor controller
int referencePin = A2; //reference Pin to compare against current, voltage and encoder pin
boolean directionOfTravel;

//LEDS
int ledPin = 9;

//IRdistance sensors
int frontIrPin = A3;
int backIrPin = A4;
int numSamples = 10;

//Conversions
double rpmMultiplier = 666.6;
double voltageMultiplier = 0.076982;
double currentMultiplier = 0.135135;
double scaleOffset = 2.5;

//Voltage Reference
bool useRef = true;
int realReference = 512;

//Watchdog
bool watchdogEnabled = false;
unsigned long watchdogTimer;
unsigned long timeoutTime = 30000;
String recallCode = "M1005";

//Timing
unsigned long lastTime = 0;

//Logging
String logs = "marsduino initated";




void setup() {
  //modifies registries to increase PWM frequency
  TCCR1B = (TCCR1B & 0b11111000) | 0x01;

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
    delay(60);
  }

  // average divided by numSamples to average, then divided by 205 to convert to voltage
  float avgVoltage = ((float) sampleSum / (float) numSamples) / 205.0;
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
  
  char codeArray[8]; //input string turned into an array
  input.toCharArray(codeArray, 6);

  //First character defines what type of command
  char first = codeArray[0];

  switch (first) {
    //Motor code
    case 'M': {
        char enable = codeArray[1] == '0' ? LOW : HIGH;
        char reverse = codeArray[2] == '0' ? LOW : HIGH;
        char brake = codeArray[3] == '0' ? LOW : HIGH;
        char speedValue = codeArray[4];

        digitalWrite(enablePin, enable); //ENABLE PIN(13)
        digitalWrite(revPin, reverse); //REVERSE PIN(7)
        digitalWrite(brakePin, brake); //NOTE BRAKE IS AN ACTIVE HIGH BRAKE PIN(12)

        //SPEED PIN(5)
        int speedDutyCycle = int(charToInt(speedValue) * 25.5); //converts input ao a 0-255 scale
        analogWrite(speedPin, speedDutyCycle); //sets up PWM on the speedPin

        //Changing the global direction for reference in the DAQ
        directionOfTravel = codeArray[2] == '0' ? 0 : 1; // one is forwards, zero is backwards
        logs = "motor code set to level to " + input.substring(1);
        break;
      }
    //LED code
    case 'L': {
        char ledValue = codeArray[1];
        int ledDutyCycle = int(charToInt(ledValue) * 25.5);
        analogWrite(ledPin, ledDutyCycle); //sets up PWM on the speedPin
        logs = "LEDs set to level to " + ledValue;
        break;
      }

    case 'R': {
      useRef = true;
      realReference = input.substring(1).toInt();
      logs = "Voltage Reference set to " + input.substring(1);
      break;
    }
    case 'E': {
      useRef = false;
      logs = "Voltage Reference disabled";
    }
    case 'W': {
      watchdogEnabled = true;
      watchdogTimer = 0;
      logs = "Watchdog Timer Reset";
      break;
    }
    case 'Q': {
      watchdogEnabled = false;
      logs = "Watchdog Timer Disabled";
    }
  }
}

/**
   Generates a DaqTelemetry object
*/
DaqTelemetry* daq()
{
  daqTelemetry = new DaqTelemetry();
  int voltageOffset;
  if(useRef == true){
    //generating an offset based off of the reference voltage sent from motor controller
    double referenceVoltage = analogRead(referencePin);
    voltageOffset = int(realReference - referenceVoltage);
  }  
  else{
    voltageOffset = 0;
  }
  
  //Motor Calculations
  double encoderVoltage = ( analogRead(encoderPin) + voltageOffset ) * 0.0049; //.0049 convert to real voltage values
  double scaledVoltage = encoderVoltage - scaleOffset;
  double finalRpm = scaledVoltage * rpmMultiplier;
  
  if((scaledVoltage < -1.5) && (scaledVoltage > -2.0)){  
    finalRpm = -1000.0;  }
  else if (scaledVoltage < -2.0){
    finalRpm = 0.0;
  }
  else if (scaledVoltage > 1.5){
    finalRpm = 1000;  }
    
  //System Voltage Calculations
  double inputV = analogRead(voltagePin) + voltageOffset;
  double finalV = inputV * voltageMultiplier;
  
  //System Current Calculations
  double inputI = analogRead(currentPin) + voltageOffset;
  double finalI = inputI * currentMultiplier;

  //Distance Calculations
  int irPin = directionOfTravel == '0' ? backIrPin : frontIrPin;
  double distance = ir_distance(irPin, voltageOffset);


 //assigning values to daqTelemetry object  
  daqTelemetry->systemRpm = finalRpm;
  daqTelemetry->systemVoltage = finalV; 
  daqTelemetry->systemCurrent = finalI;
  daqTelemetry->distance = distance;

  return daqTelemetry;
}


/**
   Send daqTelemtry data over the serial
*/

String distance_to_string(double distance){
  String outputDistance = (String)distance;
    
  if(outputDistance == "-1") {
     outputDistance = "out of range";
  }
  return outputDistance;
}


void save_and_send(DaqTelemetry *daqTelemetry)
{
  String outputDistance = distance_to_string(daqTelemetry->distance);
  
  String daqString = String(daqTelemetry->systemRpm) + "," +
                     String(daqTelemetry->systemVoltage) + "," +
                     String(daqTelemetry->systemCurrent) + "," +
                     String(outputDistance) + "," +
                     logs + "," +
                     (millis() / 1000.0 );
  Serial.println(daqString);
}

int update_watchdog_timer(){
  watchdogTimer = watchdogTimer + ( millis() - lastTime );
  lastTime = millis();
  return watchdogTimer;
}

void loop() {
  Serial.println(watchdogTimer);
  if (Serial.available() > 0) {
    process_code( retrieve_code() );
  }
  daqTelemetry = daq();
  save_and_send(daqTelemetry);
  
 update_watchdog_timer();
  if(watchdogEnabled == true){
    if(watchdogTimer > timeoutTime){
      process_code( recallCode );
    }
  }
  Serial.print("freeMemory()=");
  Serial.println(freeMemory());
  logs = "Null";
  delete daqTelemetry;
}


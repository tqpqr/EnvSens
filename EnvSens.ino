#include "SdsDustSensor.h"
#include <ArduinoJson.h>
#include <Arduino.h>
#include <Wire.h>
#include "radSens1v2.h"


int rxPin = 0;
int txPin = 1;
SdsDustSensor sds(rxPin, txPin);
ClimateGuard_RadSens1v2 radSens(RS_DEFAULT_I2C_ADDRESS); /*Constructor of the class ClimateGuard_RadSens1v2,
                                                           sets the address parameter of I2C sensor.
                                                           Default address: 0x66.*/

void setup() {
  Serial.begin(115200);
  sds.begin(); /*Starting SDS011 sensor.*/ 
  /*Serial.println(sds.queryFirmwareVersion().toString()); // prints firmware version
  Serial.println(sds.setActiveReportingMode().toString()); // ensures sensor is in 'active' reporting mode
  Serial.println(sds.setContinuousWorkingPeriod().toString()); // ensures sensor has continuous working period - default but not recommended*/ 

  radSens.radSens_init(); /*Initialization function and sensor connection. 
                            Returns false if the sensor is not connected to the I2C bus.*/
  uint8_t sensitivity = radSens.getSensitivity(); /*Rerutns the value coefficient used for calculating
                                                    the radiation intensity or 0 if sensor isn't connected.*/
  bool hvGeneratorState = radSens.getHVGeneratorState(); /*Returns state of high-voltage voltage Converter.
                                                           If return true -> on
                                                           If return false -> off or sensor isn't conneted*/
  radSens.setSensitivity(55); /*Sets the value coefficient used for calculating
                                the radiation intensity*/

  sensitivity = radSens.getSensitivity();
  /*Serial.print("\t getSensitivity(): "); Serial.println(sensitivity);
  Serial.println("\t setSensitivity(105)... ");*/

  radSens.setSensitivity(105);

  /*Serial.print("\t getSensitivity(): "); Serial.println(radSens.getSensitivity());*/

  radSens.setHVGeneratorState(true);

  hvGeneratorState = radSens.getHVGeneratorState();
  /*Serial.print("\t HV generator state: "); Serial.print(hvGeneratorState);
  Serial.println("\n-------------------------------------");*/



  }

void loop() {
  StaticJsonDocument<200> doc;
  
  PmResult pm = sds.readPm();


  float pm25 = pm.pm25; /*Number of small (pm 2.5) particles*/
  float pm10 = pm.pm10; /*Number of big (pm 10) particles*/
  float dynamicRAD = radSens.getRadIntensyDyanmic(); /*Returns radiation intensity (dynamic period T < 123 sec).*/
  float staticRAD = radSens.getRadIntensyStatic(); /*Returns radiation intensity (static period T = 500 sec).*/
  int numberRAD = radSens.getNumberOfPulses(); /*Returns the accumulated number of pulses registered by the 
                                               module since the last I2C data reading.*/
  
  int CO_level = analogRead(A0); /*Level of CO from MQ-7 Connected to A0 port*/
  bool CO_levelDig = digitalRead(4); /*Boolean CO (there is CO - 1, there is no - 0)*/
  
  
  /*doc["day"] = "Monday";*/
  doc["P2_5"] = pm25;
  doc["P10"] = pm10;
  doc["CO2_Level"] = CO_level;
  /*doc["CO Level Bool"] = CO_levelDig;*/
  doc["Rad_dynamic"] = dynamicRAD;
  doc["Rad_static"] = staticRAD;
  doc["Rad_pulses"] = numberRAD;
  serializeJson(doc, Serial);

  delay(1000);

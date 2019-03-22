// Test code for Ultimate GPS Using Hardware Serial (e.g. GPS Flora or FeatherWing)
//
// This code shows how to listen to the GPS module via polling. Best used with
// Feathers or Flora where you have hardware Serial and no interrupt
//
// Tested and works great with the Adafruit GPS FeatherWing
// ------> https://www.adafruit.com/products/3133
// or Flora GPS
// ------> https://www.adafruit.com/products/1059
// but also works with the shield, breakout
// ------> https://www.adafruit.com/products/1272
// ------> https://www.adafruit.com/products/746
// 
// Pick one up today at the Adafruit electronics shop
// and help support open source hardware & software! -ada
     
#include <Adafruit_GPS.h>
#include <Adafruit_LSM9DS0.h>
#include <Adafruit_Sensor.h>  // not used in this demo but required!

// what's the name of the hardware serial port?
#define GPSSerial Serial1

// Connect to the GPS on the hardware port
Adafruit_GPS GPS(&GPSSerial);
     
// Set GPSECHO to 'false' to turn off echoing the GPS data to the Serial console
// Set to 'true' if you want to debug and listen to the raw GPS sentences
#define GPSECHO false

uint32_t timer = millis();

int ledPin = 2 ;
int smoothAccel[16] = { 0 } ;
int smoothDiff[16] = { 0 } ;
//int uThreshold = 19000 ;
int uThreshold = 10000 ;
int bThreshold = 15000 ;

// i2c
Adafruit_LSM9DS0 lsm = Adafruit_LSM9DS0();

// You can also use software SPI
//Adafruit_LSM9DS0 lsm = Adafruit_LSM9DS0(13, 12, 11, 10, 9);
// Or hardware SPI! In this case, only CS pins are passed in
//Adafruit_LSM9DS0 lsm = Adafruit_LSM9DS0(10, 9);

void setupSensor()
{
  // 1.) Set the accelerometer range
  lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_2G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_4G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_6G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_8G);
  //lsm.setupAccel(lsm.LSM9DS0_ACCELRANGE_16G);
  
  // 2.) Set the magnetometer sensitivity
  lsm.setupMag(lsm.LSM9DS0_MAGGAIN_2GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_4GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_8GAUSS);
  //lsm.setupMag(lsm.LSM9DS0_MAGGAIN_12GAUSS);

  // 3.) Setup the gyroscope
  lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_245DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_500DPS);
  //lsm.setupGyro(lsm.LSM9DS0_GYROSCALE_2000DPS);
}
void setup()
{
  #ifndef ESP8266
  while (!Serial);     // will pause Zero, Leonardo, etc until serial console opens
#endif
  //Serial.begin(9600);
  Serial.begin(115200);
  Serial.println("Adafruit GPS library basic test!");
  Serial.println("LSM raw read demo");
  
  // Try to initialise and warn if we couldn't detect the chip
  if (!lsm.begin())
  {
    Serial.println("Oops ... unable to initialize the LSM9DS0. Check your wiring!");
    while (1);
  }
  Serial.println("Found LSM9DS0 9DOF");
  Serial.println("");
  Serial.println("");

   // Print column headings
  Serial.print("AccelX,"); 
  Serial.print("Y,");
  Serial.print("Z,");
  //Serial.print("GyroX,");
 // Serial.print("Y,");
  //Serial.print("Z,");
 // Serial.print("MagX,");
 // Serial.print("Y,");
 // Serial.print("Z,");
 // Serial.println( "T" ) ;
 Serial.print ( "current" ) ;
 Serial.print ( "," ) ;
 Serial.print ( "totalAccel" ) ;
 Serial.print ( "," ) ;
 Serial.print ( "runningAvg" ) ;
 Serial.print ( "," ) ;
 Serial.println ( "diff" ) ;
  

  //while (!Serial);  // uncomment to have the sketch wait until Serial is ready
  
  // connect at 115200 so we can read the GPS fast enough and echo without dropping chars
  // also spit it out
  
     
  // 9600 NMEA is the default baud rate for Adafruit MTK GPS's- some use 4800
  GPS.begin(9600);
  // uncomment this line to turn on RMC (recommended minimum) and GGA (fix data) including altitude
  GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCGGA);
  // uncomment this line to turn on only the "minimum recommended" data
  //GPS.sendCommand(PMTK_SET_NMEA_OUTPUT_RMCONLY);
  // For parsing data, we don't suggest using anything but either RMC only or RMC+GGA since
  // the parser doesn't care about other sentences at this time
  // Set the update rate
  GPS.sendCommand(PMTK_SET_NMEA_UPDATE_1HZ); // 1 Hz update rate
  // For the parsing code to work nicely and have time to sort thru the data, and
  // print it out we don't suggest using anything higher than 1 Hz
     
  // Request updates on antenna status, comment out to keep quiet
  GPS.sendCommand(PGCMD_ANTENNA);

  delay(1000);
  
  // Ask for firmware version
  GPSSerial.println(PMTK_Q_RELEASE);
}

void loop() // run over and over again
{
  // read data from the GPS in the 'main loop'
  char c = GPS.read();
  // if you want to debug, this is a good time to do it!
  if (GPSECHO)
    if (c) Serial.print(c);
  // if a sentence is received, we can check the checksum, parse it...
  if (GPS.newNMEAreceived()) {
    // a tricky thing here is if we print the NMEA sentence, or data
    // we end up not listening and catching other sentences!
    // so be very wary if using OUTPUT_ALLDATA and trytng to print out data
    Serial.println(GPS.lastNMEA()); // this also sets the newNMEAreceived() flag to false
    if (!GPS.parse(GPS.lastNMEA())) // this also sets the newNMEAreceived() flag to false
      return; // we can fail to parse a sentence in which case we should just wait for another
  }
  // if millis() or timer wraps around, we'll just reset it
  if (timer > millis()) timer = millis();
     
  // approximately every 2 seconds or so, print out the current stats
  if (millis() - timer > 2000) {
    timer = millis(); // reset the timer
    Serial.print("\nTime: ");
    Serial.print(GPS.hour, DEC); Serial.print(':');
    Serial.print(GPS.minute, DEC); Serial.print(':');
    Serial.print(GPS.seconds, DEC); Serial.print('.');
    Serial.println(GPS.milliseconds);
    Serial.print("Date: ");
    Serial.print(GPS.day, DEC); Serial.print('/');
    Serial.print(GPS.month, DEC); Serial.print("/20");
    Serial.println(GPS.year, DEC);
    Serial.print("Fix: "); Serial.print((int)GPS.fix);
    Serial.print(" quality: "); Serial.println((int)GPS.fixquality);
    if (GPS.fix) {
      Serial.print("Location: ");
      Serial.print(GPS.latitude, 4); Serial.print(GPS.lat);
      Serial.print(", ");
      Serial.print(GPS.longitude, 4); Serial.println(GPS.lon);
      Serial.print("Speed (knots): "); Serial.println(GPS.speed);
      Serial.print("Angle: "); Serial.println(GPS.angle);
      Serial.print("Altitude: "); Serial.println(GPS.altitude);
      Serial.print("Satellites: "); Serial.println((int)GPS.satellites);
    }
    
  }
  static int current = 0 ;
  static int totalAccel = 0 ;
  int runningAvg = 0 ;
  
  lsm.read();
 
  // print corresponding data

  // Accelerations
  /*
  Serial.print((int)lsm.accelData.x); Serial.print(",");
  Serial.print((int)lsm.accelData.y); Serial.print(",");
  Serial.print((int)lsm.accelData.z);  Serial.print(",");
*/
/*
  // Gyros
  Serial.print((int)lsm.gyroData.x);   Serial.print(",");
  Serial.print((int)lsm.gyroData.y);        Serial.print(",");
  Serial.print((int)lsm.gyroData.z);      Serial.print(",");

  // Magnetometer
  Serial.print((int)lsm.magData.x);     Serial.print(",");
  Serial.print((int)lsm.magData.y);         Serial.print(",");
  Serial.print((int)lsm.magData.z);       Serial.print(",");
  
  Serial.print((int)lsm.temperature);    Serial.print(",");
  */
  
  // add all accel values together
  //totalAccel = (int)lsm.accelData.x + (int)lsm.accelData.y + (int)lsm.accelData.z ;
  totalAccel = (int)lsm.accelData.z ;

  // Put latest value into buffer
  current ++ ;
  if ( current > 15 ) 
  {
    current = 0 ;
  }
  smoothAccel[current] = totalAccel ;
  
  // Average all elements in buffer
  for ( int i = 0 ; i < 15 ; i++ )
  {
    runningAvg += smoothAccel[i] ;
  }
  runningAvg /= 15 ;

  // subtract off smoothed trend to get peaks
  //int diff = totalAccel - runningAvg ;
  int diff = runningAvg - totalAccel ;
  // Check peak
  /*
  Serial.print ( current ) ;
  Serial.print ( "," ) ;
  Serial.print ( totalAccel ) ;
  Serial.print ( "," ) ;
  Serial.print ( runningAvg ) ;
  Serial.print ("," ) ;
  */
  Serial.print (  diff  ) ;
  
  //if ( abs ( diff ) > uThreshold || abs ( diff ) < bThreshold )
  if( abs ( diff ) > uThreshold ) 
  {
    digitalWrite ( ledPin, HIGH ) ;
    Serial.print ( "," ) ;
    //Serial.print ( 20000 ) ;
    Serial.print ( "trigger" ) ;
    delay ( 10 ) ;
  }
  else
  {
    digitalWrite ( ledPin, LOW ) ;
  }

  Serial.println ( ) ;
  delay(100);
}

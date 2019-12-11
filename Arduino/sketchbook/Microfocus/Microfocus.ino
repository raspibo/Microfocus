/*
  Controlling a servo position using a potentiometer (variable resistor)
  by Michal Rinott <http://people.interaction-ivrea.it/m.rinott>

  modified on 8 Nov 2013
  by Scott Fitzgerald
  http://www.arduino.cc/en/Tutorial/Knob
*/

#include <Servo.h>

Servo myservo;  // create servo object to control a servo

int potpin = 0;  // analog pin used to connect the potentiometer
int val = 90;  // variable to read the value from the analog pin
long last_mod = 0;

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  Serial.begin(9600);
}

void loop() {
  while (Serial.available() > 0) {
    int inp = Serial.read();
    if (inp == '+') {
      if (val <= 255) {
        val++;
        last_mod = millis();
      }
    }
    if (inp == '-') {
      if (val >= 1) {
        val--;
        last_mod = millis();
      }
    }
    if (val > 0) {
      if (val < 255) {
        myservo.attach(9);  // attaches the servo on pin 9 to the servo object
        myservo.write(val);                  // sets the servo position according to the scaled value
        Serial.print("valore: ");
        Serial.println(val);
      }
    }
    delay(15);                           // waits for the servo to get there
  }
  if (millis() > last_mod + 3000) {
    myservo.detach();
  }
}


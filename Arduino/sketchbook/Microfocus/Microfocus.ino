
#include <IRremote.h>

int RECV_PIN = 11;

IRrecv irrecv(RECV_PIN);

decode_results results;


#include <Servo.h>


Servo myservo;      // create servo object to control a servo
int inp = 0;        // value read from serial port
int ir = 0;         // value read from infrared
int last_ir = 0;    // last value read from infrared (some ir commands after first button press repeat a sequence of 0xFFFFFFFF, last_ir contain last first pressed button)
int val = 90;       // variable to read the value from the analog pin
int last_val = 0;   // variable to store last val (last position of servo) used to reduce serial prints
long last_mod = 0;  // store last pos change time to activate power saving
#define POWERSAVE_MILLIS 3000

void setup() {
  myservo.attach(9);  // attaches the servo on pin 9 to the servo object
  Serial.begin(9600);
  irrecv.enableIRIn(); // Start the infrared receiver
}

void loop() {
  if (irrecv.decode(&results)) {
    //Serial.println(results.value, HEX); // Debug for setup
    irrecv.resume(); // Receive the next value
    if (results.value == 0x1FE08F7) {     // Up button on direction cross keys
      ir = '+';
      last_ir = ir;
    }
    if (results.value == 0x1FE10EF) {     // Down button on direction cross keys
      ir = '-';
      last_ir = ir;
    }
    if (results.value == 0xFFFFFFFF) {    // Code of last key repeat
      ir = last_ir;
    }
  }
  while (Serial.available() > 0) {
    inp = Serial.read();
  }
  if (inp == '+' or ir == '+') {
    if (val <= 255) {
      val++;
      last_mod = millis();
    }
  }
  if (inp == '-' or ir == '-') {
    if (val >= 1) {
      val--;
      last_mod = millis();
    }
  }
  if (val > 0) {
    if (val < 255) {
      myservo.attach(9);  // attaches the servo on pin 9 to the servo object
      myservo.write(val);                  // sets the servo position according to the scaled value
      if (val != last_val) {
        Serial.print("valore: ");
        Serial.println(val);
        last_val = val;
      }
    }
  }
  delay(15);                           // waits for the servo to get there
  ir = 0;
  inp = 0;

  if (millis() > last_mod + POWERSAVE_MILLIS) {
    myservo.detach();
  }
}

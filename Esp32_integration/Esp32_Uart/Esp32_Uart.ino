#define TxPin 17
#define RxPin 16

// String recMsg = "";
HardwareSerial myUart(2);

void setup() {
  Serial.begin(115200);

  myUart.begin(115200, SERIAL_8N1, RxPin, TxPin);
  Serial.println("Uart has intialized.");

}

void loop() {
  // Check if data is available to read
  if (myUart.available() > 0) {
    // Read data and display it
    String message = myUart.readStringUntil('\r');
    message.trim();
    Serial.println("Received: " + message);
    delay(1000);
  }
}




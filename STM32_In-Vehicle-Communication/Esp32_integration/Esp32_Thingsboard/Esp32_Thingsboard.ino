#include <WiFi.h>
#include<WiFiClient.h>
#include <HTTPClient.h>

#define TxPin 17
#define RxPin 16

HardwareSerial myUart(2);

char *ssid = "Shreesaipg 402";
char *password = "shreesaipg402";
String body = "";
WiFiClient client;
HTTPClient httpClient;

void setup() {
  Serial.begin(115200);
  Serial.flush();
  
  myUart.begin(115200, SERIAL_8N1, RxPin, TxPin);
  Serial.println("Uart has intialized.");

  // Modes -- STA (station) / AP (Access Point)
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi ");
  while(WiFi.status() != WL_CONNECTED){
    delay(500);
    Serial.print(".");
  }

  Serial.println("Connected To WiFi");
  Serial.print("IP Address : ");
  Serial.println(WiFi.localIP());

  Serial.println("Setup is completed");
  httpClient.begin(client, "http://thingsboard.cloud/api/v1/FZsLXt7l4ry0ODSn9gE0/telemetry");

}

void loop() {

    if (myUart.available() > 0) {
    // Read data and display it
    body = myUart.readStringUntil('\r');
    body.trim();
    Serial.println("Received: " + body);
    delay(1000);
  }
  
  Serial.println("JSON Object : " + body);

  httpClient.addHeader("Content-Type", "application/JSON");

  int status = httpClient.POST(body);

  Serial.println("Status : " + String(status));
  
 delay(500);
}
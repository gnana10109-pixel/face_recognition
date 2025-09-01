#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// WiFi credentials - UPDATE THESE
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Render server details - UPDATE WITH YOUR RENDER URL
const char* serverUrl = "https://your-app-name.onrender.com";
const char* resultEndpoint = "/api/arduino/result";

// Pin definitions
const int SERVO_PIN = 13;  // GPIO 13 for servo control

// Servo object
Servo doorServo;

// Variables
bool isLocked = true;
int currentAngle = 0;
unsigned long lastCheck = 0;
const unsigned long CHECK_INTERVAL = 10000;    // Check every 10 seconds

void setup() {
  Serial.begin(115200);
  
  // Initialize servo
  doorServo.attach(SERVO_PIN);
  doorServo.write(0); // Start in locked position
  
  // Connect to WiFi
  connectToWiFi();
  
  Serial.println("Setup complete!");
  Serial.println("Server URL: " + String(serverUrl));
}

void loop() {
  // Check WiFi connection
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("WiFi connection lost. Reconnecting...");
    connectToWiFi();
    return;
  }
  
  // Check for face recognition results
  if (millis() - lastCheck >= CHECK_INTERVAL) {
    checkFaceRecognition();
    lastCheck = millis();
  }
  
  delay(100);
}

void connectToWiFi() {
  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("");
  Serial.println("WiFi connected!");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void checkFaceRecognition() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    
    // Get latest result from Render
    http.begin(serverUrl + String(resultEndpoint));
    http.addHeader("Content-Type", "application/json");
    
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println("Response: " + response);
      
      // Parse JSON response
      DynamicJsonDocument doc(1024);
      DeserializationError error = deserializeJson(doc, response);
      
      if (!error) {
        String result = doc["result"];
        bool fresh = doc["fresh"];
        
        // Only process fresh results
        if (fresh) {
          if (result == "matched") {
            Serial.println("Face MATCHED - Unlocking door");
            unlockDoor();
          } else if (result == "not matched") {
            Serial.println("Face NOT MATCHED - Keeping door locked");
            lockDoor();
          }
        }
      }
    } else {
      Serial.println("HTTP Error: " + String(httpResponseCode));
    }
    
    http.end();
  }
}

void unlockDoor() {
  if (isLocked) {
    Serial.println("Unlocking door...");
    doorServo.write(90);  // Move to 90 degrees (unlocked)
    currentAngle = 90;
    isLocked = false;
    Serial.println("Door unlocked!");
    
    // Keep door unlocked for 10 seconds, then relock
    delay(10000);
    lockDoor();
  }
}

void lockDoor() {
  if (!isLocked) {
    Serial.println("Locking door...");
    doorServo.write(0);   // Move to 0 degrees (locked)
    currentAngle = 0;
    isLocked = true;
    Serial.println("Door locked!");
  }
}

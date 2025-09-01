# 🚀 Complete Deployment Guide for Face Recognition Door Lock

## 📋 Prerequisites

- GitHub account
- Render account (free tier available)
- MongoDB Atlas account
- ESP32 development board
- USB camera

## 🔧 Step 1: Prepare Your Environment

### 1.1 Create Environment File
Copy `env.example` to `.env` and fill in your values:

```bash
cp env.example .env
```

Edit `.env` with your actual values:
```env
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=your-super-secret-key-change-this-in-production

# MongoDB Configuration
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority&appName=your-app-name

# Admin Credentials
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-secure-admin-password

# Server Configuration
HOST=0.0.0.0
PORT=5000

# Face Recognition Settings
FACE_TOLERANCE=0.6
RECOGNITION_TIMEOUT=30

# Arduino Communication Settings
ARDUINO_CHECK_INTERVAL=60
ARDUINO_TIMEOUT=300
```

### 1.2 MongoDB Atlas Setup
1. Go to [MongoDB Atlas](https://www.mongodb.com/atlas)
2. Create a free cluster
3. Create a database user
4. Get your connection string
5. Update `MONGO_URI` in your `.env` file

## 🚀 Step 2: Deploy to Render

### 2.1 Push to GitHub
```bash
git init
git add .
git commit -m "Initial commit for deployment"
git branch -M main
git remote add origin https://github.com/yourusername/face-recognition-door-lock.git
git push -u origin main
```

### 2.2 Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:
   - **Name**: `face-recognition-door-lock`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free

### 2.3 Environment Variables in Render
Add these environment variables in Render dashboard:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `your-super-secret-key` |
| `MONGO_URI` | `your-mongodb-connection-string` |
| `ADMIN_USERNAME` | `admin` |
| `ADMIN_PASSWORD` | `your-secure-password` |
| `FACE_TOLERANCE` | `0.6` |
| `RECOGNITION_TIMEOUT` | `30` |

### 2.4 Deploy
Click "Create Web Service" and wait for deployment (5-10 minutes).

## 🔌 Step 3: Update ESP32 Code

### 3.1 Get Your Render URL
After deployment, you'll get a URL like: `https://face-recognition-door-lock.onrender.com`

### 3.2 Update ESP32 Code
Edit `esp32_face_lock.ino`:

```cpp
// Replace this line:
const char* serverUrl = "http://YOUR_COMPUTER_IP:5000";

// With your Render URL:
const char* serverUrl = "https://your-app-name.onrender.com";
```

### 3.3 Complete ESP32 Code for Render
```cpp
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>
#include <ESP32Servo.h>

// WiFi credentials
const char* ssid = "YOUR_WIFI_SSID";
const char* password = "YOUR_WIFI_PASSWORD";

// Render server details
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
const unsigned long CHECK_INTERVAL = 5000;    // Check every 5 seconds

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
```

## 🧪 Step 4: Test Your Deployment

### 4.1 Test Web Interface
1. Visit your Render URL: `https://your-app-name.onrender.com`
2. Test face recognition functionality
3. Access admin dashboard with your credentials

### 4.2 Test Arduino Communication
1. Upload the updated ESP32 code
2. Open Serial Monitor (115200 baud)
3. Check for successful WiFi connection
4. Verify HTTP requests to your Render URL
5. Test face recognition and servo control

## 🔍 Step 5: Monitoring and Debugging

### 5.1 Render Logs
- Go to your Render dashboard
- Click on your service
- View "Logs" tab for real-time logs

### 5.2 ESP32 Serial Monitor
Monitor ESP32 output for:
- WiFi connection status
- HTTP response codes
- Face recognition results
- Servo control actions

### 5.3 Common Issues and Solutions

#### Issue: ESP32 can't connect to Render
**Solution**: 
- Check WiFi credentials
- Verify Render URL is correct
- Ensure HTTPS is used (not HTTP)

#### Issue: Face recognition not working
**Solution**:
- Check MongoDB connection
- Verify face encodings are stored
- Test with admin dashboard

#### Issue: Servo not moving
**Solution**:
- Check servo wiring
- Verify power supply
- Test servo with simple code

## 🎯 Step 6: Production Optimization

### 6.1 Security Enhancements
- Change default admin credentials
- Use strong SECRET_KEY
- Enable HTTPS (automatic with Render)
- Restrict MongoDB access

### 6.2 Performance Optimization
- Use Render's paid plans for better performance
- Optimize face recognition tolerance
- Implement caching for face encodings

### 6.3 Monitoring
- Set up Render alerts
- Monitor MongoDB Atlas metrics
- Track face recognition accuracy

## 📱 Step 7: Mobile Access

Your deployed system is now accessible from anywhere:
- **Web Interface**: `https://your-app-name.onrender.com`
- **Admin Dashboard**: `https://your-app-name.onrender.com/dashboard`
- **API Endpoints**: Available for mobile app integration

## 🔄 Step 8: Updates and Maintenance

### 8.1 Code Updates
1. Make changes locally
2. Test thoroughly
3. Push to GitHub
4. Render auto-deploys

### 8.2 Database Management
- Use MongoDB Atlas dashboard
- Monitor storage usage
- Backup face encodings regularly

## ✅ Deployment Checklist

- [ ] Environment variables configured
- [ ] MongoDB Atlas setup complete
- [ ] Code pushed to GitHub
- [ ] Render service deployed
- [ ] ESP32 code updated with Render URL
- [ ] WiFi credentials configured
- [ ] Servo motor connected
- [ ] Web interface tested
- [ ] Arduino communication verified
- [ ] Face recognition working
- [ ] Admin dashboard accessible

## 🎉 Congratulations!

Your face recognition door lock system is now deployed and accessible from anywhere in the world! The ESP32 can communicate with your cloud-hosted Flask application, making it a truly IoT-enabled security system.

## 📞 Support

If you encounter any issues:
1. Check Render logs
2. Monitor ESP32 serial output
3. Verify MongoDB connection
4. Test API endpoints manually

Happy coding! 🚀

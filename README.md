# Face Recognition Door Lock System

A secure door lock system that uses facial recognition technology to control access. The system consists of a Flask web application for face management and an ESP32 microcontroller for servo motor control.

## Features

- **Face Recognition**: Real-time face detection and recognition using OpenCV and face_recognition library
- **Web Interface**: Beautiful landing page with camera integration and admin dashboard
- **Database Storage**: MongoDB Atlas integration for storing face encodings
- **Arduino Integration**: ESP32 with servo motor control for door lock mechanism
- **Responsive Design**: Modern UI built with Tailwind CSS
- **Secure Access**: Admin login system for managing face encodings

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Camera    │    │   Flask App     │    │   MongoDB       │
│   (Frontend)    │───▶│   (Backend)     │───▶│   Atlas         │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   ESP32         │
                       │   + Servo       │
                       │   Motor         │
                       └─────────────────┘
```

## Prerequisites

- Python 3.8 or higher
- ESP32 development board
- SG90 or similar servo motor
- Web camera (USB camera recommended)
- WiFi network
- MongoDB Atlas account

## Installation

### 1. Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. MongoDB Setup

1. Create a MongoDB Atlas account
2. Create a new cluster
3. Get your connection string
4. Update the `MONGO_URI` in `app.py` with your connection string

### 3. ESP32 Setup

1. Install Arduino IDE
2. Add ESP32 board support
3. Install required libraries:
   - WiFi
   - HTTPClient
   - ArduinoJson
   - Servo

## Configuration

### Flask Application

1. Update MongoDB connection string in `app.py`
2. Modify admin credentials if needed (default: admin/123456)
3. Set your computer's IP address for ESP32 communication

### ESP32 Configuration

1. Update WiFi credentials in `esp32_face_lock.ino`:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```

2. Update Flask server URL:
   ```cpp
   const char* serverUrl = "http://YOUR_COMPUTER_IP:5000";
   ```

3. Configure servo pin (default: GPIO 13):
   ```cpp
   const int SERVO_PIN = 13;
   ```

## Usage

### Starting the Flask Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

### USB Camera Setup

1. **Connect your USB camera** to your computer
2. **Install camera drivers** if required by your operating system
3. **Test camera access** using the provided test script:
   ```bash
   python test_usb_camera.py
   ```
4. **Access the web interface** - cameras will be automatically detected
5. **Select your USB camera** from the dropdown menu (USB cameras are marked with 🔌)
6. **Use the "Refresh Cameras" button** if your camera isn't detected initially

**Note**: USB cameras are automatically prioritized and will be pre-selected when available.

### Landing Page

- **Face Recognition**: Click "Capture & Recognize" to identify faces
- **Real-time Results**: Shows "MATCHED" or "NOT MATCHED" status
- **Admin Login**: Bottom-right button to access dashboard

### Admin Dashboard

- **Add Faces**: Capture and store new face encodings
- **Manage Database**: View and delete registered faces
- **Access Control**: Secure admin-only access

### ESP32 Operation

1. Upload the Arduino code to ESP32
2. Connect servo motor to GPIO 13
3. Power on the ESP32
4. The system will automatically:
   - Connect to WiFi
   - Poll Flask server for recognition results
   - Control servo motor based on face match status

## Hardware Connections

### ESP32 Pinout

```
ESP32 Pin    Component
─────────    ─────────
GPIO 13      Servo Signal (Orange/Yellow)
GPIO 2       Status LED
GPIO 4       Buzzer (Optional)
3.3V         Servo Power (Red)
GND          Servo Ground (Brown)
```

### Servo Motor

- **Red Wire**: 3.3V or 5V power supply
- **Brown/Black Wire**: Ground (GND)
- **Orange/Yellow Wire**: Signal (GPIO 13)

## API Endpoints

### Flask Routes

- `GET /` - Landing page
- `POST /login` - Admin authentication
- `GET /dashboard` - Admin dashboard
- `POST /add_face` - Add new face encoding
- `POST /delete_face` - Delete face encoding
- `POST /recognize_face` - Face recognition
- `POST /api/check_face` - Arduino communication endpoint

### Response Format

```json
{
  "result": "matched|not matched",
  "message": "Description",
  "name": "Person name (if matched)"
}
```

## Security Features

- Session-based authentication
- Admin-only access to face management
- Secure MongoDB connection
- Input validation and sanitization

## Troubleshooting

### Common Issues

1. **Camera Access Denied**
   - Ensure browser has camera permissions
   - Check HTTPS requirement for some browsers
   - For USB cameras: ensure proper drivers are installed
   - Try refreshing the camera list using the "Refresh Cameras" button

2. **MongoDB Connection Error**
   - Verify connection string
   - Check network connectivity
   - Ensure IP whitelist includes your IP

3. **ESP32 Connection Issues**
   - Verify WiFi credentials
   - Check Flask server IP address
   - Ensure both devices are on same network

4. **Servo Motor Problems**
   - Check power supply (3.3V or 5V)
   - Verify wiring connections
   - Test with simple servo sweep code

### Debug Mode

Enable debug mode in Flask:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```

### Camera Troubleshooting

If you're having issues with your USB camera:

1. **Test camera access**:
   ```bash
   python test_usb_camera.py
   ```

2. **Check camera permissions** in your browser:
   - Chrome: Settings → Privacy and security → Site Settings → Camera
   - Firefox: Settings → Privacy & Security → Permissions → Camera
   - Edge: Settings → Cookies and site permissions → Camera

3. **Verify camera drivers**:
   - Windows: Device Manager → Imaging devices
   - macOS: System Information → USB
   - Linux: `lsusb` command

4. **Try different USB ports** if available

5. **Check browser console** for error messages

## Customization

### Face Recognition Sensitivity

Adjust tolerance in `app.py`:
```python
matches = face_recognition.compare_faces([stored_encoding], face_encodings[0], tolerance=0.6)
```

### Servo Angles

Modify servo positions in ESP32 code:
```cpp
void unlockDoor() {
  doorServo.write(90);  // Unlocked position
}

void lockDoor() {
  doorServo.write(0);   // Locked position
}
```

### Check Interval

Change polling frequency:
```cpp
const unsigned long CHECK_INTERVAL = 5000; // 5 seconds
```

## Performance Optimization

- Reduce image resolution for faster processing
- Implement face detection caching
- Use background processing for recognition
- Optimize MongoDB queries

## Future Enhancements

- Real-time video streaming
- Multiple camera support
- Face liveness detection
- Mobile app integration
- Cloud-based face recognition
- Access logging and analytics

## License

This project is open source and available under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review error logs in Flask console
3. Monitor ESP32 serial output
4. Verify network connectivity

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

#!/usr/bin/env python3
"""
Test script for Face Recognition Door Lock System
Tests Flask endpoints and Arduino communication
"""

import requests
import json
import time
import base64
from PIL import Image
import numpy as np

# Flask server configuration
BASE_URL = "http://localhost:5000"

def test_server_connection():
    """Test if Flask server is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Flask server is running")
            return True
        else:
            print(f"❌ Flask server returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask server. Is it running?")
        return False

def test_arduino_endpoints():
    """Test Arduino communication endpoints"""
    print("\n🔌 Testing Arduino endpoints...")
    
    # Test status endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/arduino/status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Status endpoint: {data}")
        else:
            print(f"❌ Status endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Status endpoint error: {e}")
    
    # Test result endpoint
    try:
        response = requests.get(f"{BASE_URL}/api/arduino/result")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Result endpoint: {data}")
        else:
            print(f"❌ Result endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Result endpoint error: {e}")
    
    # Test heartbeat endpoint
    try:
        response = requests.post(f"{BASE_URL}/api/arduino/heartbeat", json={})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Heartbeat endpoint: {data}")
        else:
            print(f"❌ Heartbeat endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Heartbeat endpoint error: {e}")

def test_servo_control():
    """Test servo control endpoint"""
    print("\n⚙️ Testing servo control...")
    
    test_angles = [0, 90, 180, 0]
    
    for angle in test_angles:
        try:
            response = requests.post(f"{BASE_URL}/api/arduino/test_servo", 
                                  json={"angle": angle})
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Servo {angle}°: {data['message']}")
            else:
                print(f"❌ Servo {angle}° failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Servo {angle}° error: {e}")
        
        time.sleep(1)

def create_test_image():
    """Create a simple test image for face recognition"""
    # Create a 100x100 test image
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Convert to base64
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    return f"data:image/jpeg;base64,{img_str}"

def test_face_recognition():
    """Test face recognition endpoint"""
    print("\n👤 Testing face recognition...")
    
    # Create test image
    test_image = create_test_image()
    
    try:
        response = requests.post(f"{BASE_URL}/recognize_face", 
                              data={"image": test_image})
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Face recognition: {data}")
        else:
            print(f"❌ Face recognition failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Face recognition error: {e}")

def test_admin_login():
    """Test admin login functionality"""
    print("\n🔐 Testing admin login...")
    
    # Test with correct credentials
    try:
        response = requests.post(f"{BASE_URL}/login", 
                              data={"username": "admin", "password": "123456"})
        if response.status_code == 302:  # Redirect to dashboard
            print("✅ Admin login successful")
        else:
            print(f"❌ Admin login failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Admin login error: {e}")
    
    # Test with wrong credentials
    try:
        response = requests.post(f"{BASE_URL}/login", 
                              data={"username": "admin", "password": "wrong"})
        if response.status_code == 200:  # Stay on login page
            print("✅ Wrong credentials handled correctly")
        else:
            print(f"❌ Wrong credentials not handled: {response.status_code}")
    except Exception as e:
        print(f"❌ Wrong credentials test error: {e}")

def main():
    """Main test function"""
    print("🚀 Face Recognition Door Lock System - Test Suite")
    print("=" * 50)
    
    # Test server connection
    if not test_server_connection():
        print("\n❌ Server connection failed. Please start the Flask application first.")
        print("Run: python app.py")
        return
    
    # Test all endpoints
    test_arduino_endpoints()
    test_servo_control()
    test_face_recognition()
    test_admin_login()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n📋 Next steps:")
    print("1. Upload esp32_face_lock.ino to your ESP32")
    print("2. Update WiFi credentials and server IP in the Arduino code")
    print("3. Connect servo motor to GPIO 13")
    print("4. Test the complete system!")

if __name__ == "__main__":
    import io
    main()

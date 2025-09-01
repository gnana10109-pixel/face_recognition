from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import face_recognition
import cv2
import numpy as np
from PIL import Image
import io
import base64
import pymongo
from datetime import datetime
import os
import threading
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI', "mongodb+srv://gnana:Abcd1234@face.7yfuxi6.mongodb.net/?retryWrites=true&w=majority&appName=face")
client = pymongo.MongoClient(MONGO_URI)
db = client.face_recognition_db
face_collection = db.faces

# Admin credentials from environment
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', '123456')

# Face recognition settings
FACE_TOLERANCE = float(os.getenv('FACE_TOLERANCE', '0.6'))
RECOGNITION_TIMEOUT = int(os.getenv('RECOGNITION_TIMEOUT', '30'))

# Global variables for Arduino communication
last_recognition_result = None
last_recognition_time = None
arduino_status = "disconnected"

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session['logged_in'] = True
        return redirect(url_for('dashboard'))
    else:
        return render_template('landing.html', error="Invalid credentials")

@app.route('/dashboard')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('landing'))
    
    faces = list(face_collection.find({}, {'_id': 0}))
    return render_template('dashboard.html', faces=faces)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('landing'))

@app.route('/add_face', methods=['POST'])
def add_face():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        name = request.form.get('name')
        image_data = request.form.get('image')
        
        if not name or not image_data:
            return jsonify({'error': 'Name and image are required'}), 400
        
        # Remove data URL prefix
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Get face encodings
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            return jsonify({'error': 'No face detected in the image'}), 400
        
        # Use the first face encoding
        face_encoding = face_encodings[0].tolist()
        
        # Store in MongoDB
        face_data = {
            'name': name,
            'encoding': face_encoding,
            'created_at': datetime.now()
        }
        
        face_collection.insert_one(face_data)
        
        return jsonify({'success': True, 'message': f'Face encoding for {name} added successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/delete_face', methods=['POST'])
def delete_face():
    if not session.get('logged_in'):
        return jsonify({'error': 'Not authenticated'}), 401
    
    try:
        name = request.form.get('name')
        face_collection.delete_one({'name': name})
        return jsonify({'success': True, 'message': f'Face encoding for {name} deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/recognize_face', methods=['POST'])
def recognize_face():
    global last_recognition_result, last_recognition_time
    
    try:
        image_data = request.form.get('image')
        
        if not image_data:
            return jsonify({'error': 'Image is required'}), 400
        
        # Remove data URL prefix
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)
        
        # Convert to PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert('RGB')
        
        # Convert to numpy array
        image_array = np.array(image)
        
        # Get face encodings from uploaded image
        face_encodings = face_recognition.face_encodings(image_array)
        
        if not face_encodings:
            last_recognition_result = 'not matched'
            last_recognition_time = datetime.now()
            return jsonify({'result': 'not matched', 'message': 'No face detected'})
        
        # Get all stored face encodings
        stored_faces = list(face_collection.find({}, {'_id': 0}))
        
        if not stored_faces:
            last_recognition_result = 'not matched'
            last_recognition_time = datetime.now()
            return jsonify({'result': 'not matched', 'message': 'No faces in database'})
        
        # Compare with stored faces
        for stored_face in stored_faces:
            stored_encoding = np.array(stored_face['encoding'])
            
            # Compare faces with tolerance
            matches = face_recognition.compare_faces([stored_encoding], face_encodings[0], tolerance=FACE_TOLERANCE)
            
            if matches[0]:
                last_recognition_result = 'matched'
                last_recognition_time = datetime.now()
                return jsonify({
                    'result': 'matched',
                    'message': f'Face matched with {stored_face["name"]}',
                    'name': stored_face['name']
                })
        
        last_recognition_result = 'not matched'
        last_recognition_time = datetime.now()
        return jsonify({'result': 'not matched', 'message': 'Face not recognized'})
        
    except Exception as e:
        last_recognition_result = 'error'
        last_recognition_time = datetime.now()
        return jsonify({'error': str(e)}), 500

@app.route('/api/arduino/status', methods=['GET'])
def arduino_status_endpoint():
    """Get current Arduino status and last recognition result"""
    global last_recognition_result, last_recognition_time, arduino_status
    
    return jsonify({
        'status': arduino_status,
        'last_result': last_recognition_result,
        'last_recognition_time': last_recognition_time.isoformat() if last_recognition_time else None,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/arduino/heartbeat', methods=['POST'])
def arduino_heartbeat():
    """Arduino sends heartbeat to confirm connection"""
    global arduino_status
    arduino_status = "connected"
    
    return jsonify({
        'status': 'ok',
        'message': 'Heartbeat received',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/arduino/result', methods=['GET'])
def get_latest_result():
    """Arduino can poll this endpoint to get the latest recognition result"""
    global last_recognition_result, last_recognition_time
    
    if last_recognition_result and last_recognition_time:
        # Check if result is recent (within configured timeout)
        time_diff = (datetime.now() - last_recognition_time).total_seconds()
        
        if time_diff <= RECOGNITION_TIMEOUT:
            return jsonify({
                'result': last_recognition_result,
                'timestamp': last_recognition_time.isoformat(),
                'fresh': True
            })
        else:
            return jsonify({
                'result': 'no_recent_recognition',
                'timestamp': last_recognition_time.isoformat(),
                'fresh': False
            })
    else:
        return jsonify({
            'result': 'no_recognition_yet',
            'timestamp': None,
            'fresh': False
        })

@app.route('/api/arduino/clear_result', methods=['POST'])
def clear_recognition_result():
    """Clear the last recognition result (useful for Arduino after processing)"""
    global last_recognition_result, last_recognition_time
    
    last_recognition_result = None
    last_recognition_time = None
    
    return jsonify({
        'status': 'ok',
        'message': 'Recognition result cleared'
    })

@app.route('/api/arduino/test_servo', methods=['POST'])
def test_servo():
    """Test endpoint for servo control"""
    data = request.get_json()
    angle = data.get('angle', 0)
    
    if 0 <= angle <= 180:
        return jsonify({
            'status': 'ok',
            'message': f'Servo test command received: {angle} degrees',
            'command': f'SERVO:{angle}'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Invalid angle. Must be between 0 and 180 degrees.'
        }), 400

@app.route('/api/camera/status', methods=['GET'])
def camera_status():
    """Get camera status and information"""
    try:
        # This endpoint can be used to check camera availability
        # In a real implementation, you might want to check OpenCV camera availability
        return jsonify({
            'status': 'available',
            'message': 'Camera system ready',
            'timestamp': datetime.now().isoformat(),
            'note': 'Frontend handles camera enumeration via getUserMedia API'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Background thread to update Arduino status
def update_arduino_status():
    global arduino_status
    check_interval = int(os.getenv('ARDUINO_CHECK_INTERVAL', '60'))
    while True:
        time.sleep(check_interval)  # Check every configured interval
        if last_recognition_time:
            time_diff = (datetime.now() - last_recognition_time).total_seconds()
            if time_diff > 300:  # 5 minutes
                arduino_status = "idle"
        else:
            arduino_status = "waiting"

# Start background thread
status_thread = threading.Thread(target=update_arduino_status, daemon=True)
status_thread.start()

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)

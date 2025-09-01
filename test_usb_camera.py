#!/usr/bin/env python3
"""
Test script to verify USB camera functionality
This script helps test if your USB camera is properly detected and accessible
"""

import cv2
import sys

def test_cameras():
    """Test all available cameras"""
    print("Testing USB Camera Access...")
    print("=" * 40)
    
    # Test cameras from index 0 to 9
    for i in range(10):
        print(f"\nTesting camera index {i}...")
        
        try:
            # Try to open camera
            cap = cv2.VideoCapture(i)
            
            if not cap.isOpened():
                print(f"  ❌ Camera {i}: Not accessible")
                continue
            
            # Try to read a frame
            ret, frame = cap.read()
            
            if ret:
                # Get camera properties
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                fps = cap.get(cv2.CAP_PROP_FPS)
                
                print(f"  ✅ Camera {i}: Working")
                print(f"     Resolution: {width}x{height}")
                print(f"     FPS: {fps:.1f}")
                
                # Show a preview frame
                cv2.imshow(f'Camera {i} Preview', frame)
                print(f"     Press any key to continue...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                
            else:
                print(f"  ❌ Camera {i}: Cannot read frames")
            
            # Release camera
            cap.release()
            
        except Exception as e:
            print(f"  ❌ Camera {i}: Error - {str(e)}")
    
    print("\n" + "=" * 40)
    print("Camera testing complete!")
    print("\nTo use a specific camera in your Flask app:")
    print("1. Note the working camera index from above")
    print("2. The web interface will automatically detect and list available cameras")
    print("3. USB cameras are automatically prioritized and marked with 🔌")

def test_specific_camera(camera_index):
    """Test a specific camera index"""
    print(f"Testing specific camera index {camera_index}...")
    
    try:
        cap = cv2.VideoCapture(camera_index)
        
        if not cap.isOpened():
            print(f"❌ Camera {camera_index} is not accessible")
            return False
        
        # Read and display frames for 5 seconds
        start_time = cv2.getTickCount()
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Display frame
            cv2.imshow(f'Camera {camera_index} Test', frame)
            frame_count += 1
            
            # Check if 5 seconds have passed
            elapsed_time = (cv2.getTickCount() - start_time) / cv2.getTickFrequency()
            if elapsed_time >= 5:
                break
            
            # Break on 'q' key press
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cap.release()
        cv2.destroyAllWindows()
        
        fps = frame_count / elapsed_time
        print(f"✅ Camera {camera_index} test successful!")
        print(f"   Frames captured: {frame_count}")
        print(f"   Average FPS: {fps:.1f}")
        return True
        
    except Exception as e:
        print(f"❌ Error testing camera {camera_index}: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Test specific camera
        try:
            camera_index = int(sys.argv[1])
            test_specific_camera(camera_index)
        except ValueError:
            print("Please provide a valid camera index (integer)")
            sys.exit(1)
    else:
        # Test all cameras
        test_cameras()

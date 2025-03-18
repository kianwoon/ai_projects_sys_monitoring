"""
Camera handling functions for service monitoring
"""
import cv2
import re

class CameraManager:
    """Manages camera operations for the monitoring system"""
    
    def __init__(self):
        self.camera = None
    
    def list_cameras(self):
        """
        List all available cameras and their working status
        
        Returns:
            list: List of tuples (camera_id, camera_name)
        """
        available_cameras = []
        for i in range(10):  # Check first 10 indexes
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                ret, frame = cap.read()
                if ret:
                    camera_name = f"Camera {i}"
                    try:
                        # Try to get camera name (works on some systems)
                        cap.set(cv2.CAP_PROP_SETTINGS, 1)
                    except:
                        pass
                    available_cameras.append((i, camera_name))
                cap.release()
        return available_cameras
    
    def initialize_camera(self, camera_id_or_string):
        """
        Initialize a camera by ID or string representation
        
        Args:
            camera_id_or_string: Camera ID (int) or string like "Camera 0 (ID: 0)"
            
        Returns:
            bool: True if camera was initialized successfully
        """
        # If passed a string like "Camera 0 (ID: 0)", extract the ID
        if isinstance(camera_id_or_string, str):
            match = re.search(r'ID: (\d+)', camera_id_or_string)
            if match:
                camera_id = int(match.group(1))
            else:
                try:
                    camera_id = int(camera_id_or_string)
                except ValueError:
                    print(f"Invalid camera identifier: {camera_id_or_string}")
                    return False
        else:
            camera_id = camera_id_or_string
        
        # Close any previously opened camera
        self.release_camera()
        
        # Initialize new camera
        try:
            # Check if we're on macOS to handle Continuity Camera properly
            import platform
            if platform.system() == 'Darwin':  # macOS
                # On macOS, we need to use AVFoundation backend
                self.camera = cv2.VideoCapture(camera_id, cv2.CAP_AVFOUNDATION)
                
                # Set properties for Continuity Camera if available
                # This is to address the warning about deprecated AVCaptureDeviceTypeExternal
                # by using AVCaptureDeviceTypeContinuityCamera instead
                try:
                    # This property is specific to AVFoundation backend on macOS
                    # It tells OpenCV to use AVCaptureDeviceTypeContinuityCamera for external cameras
                    self.camera.set(cv2.CAP_PROP_SETTINGS, 1)
                except Exception as e:
                    print(f"Note: Could not set Continuity Camera properties: {e}")
            else:
                # For other platforms, use the default or V4L2 backend
                self.camera = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
                
            if not self.camera.isOpened():
                print(f"Failed to open camera {camera_id}")
                return False
            return True
        except Exception as e:
            print(f"Error initializing camera {camera_id}: {str(e)}")
            return False
    
    def capture_frame(self):
        """
        Capture a frame from the initialized camera
        
        Returns:
            numpy.ndarray: Captured frame or None if capture failed
        """
        if self.camera is None or not self.camera.isOpened():
            print("Camera not initialized")
            return None
            
        ret, frame = self.camera.read()
        if not ret:
            print("Failed to capture frame")
            return None
            
        return frame
    
    def release_camera(self):
        """Release the currently initialized camera"""
        if self.camera is not None:
            self.camera.release()
            self.camera = None
"""
Main dashboard monitoring module that integrates all components
"""
import os
import time
import tkinter as tk
from datetime import datetime
from pathlib import Path

from config_manager import ConfigManager
from camera import CameraManager
from image_processor import ImageProcessor
from alerts import AlertManager
from dashboard_ui import DashboardUI
from alert_config_ui import AlertConfigUI

class DashboardMonitor:
    """Main class that integrates all components of the monitoring system"""
    
    def __init__(self):
        """Initialize the dashboard monitor components"""
        # Initialize component managers
        self.config_manager = ConfigManager()
        self.camera_manager = CameraManager()
        self.image_processor = ImageProcessor()
        self.alert_manager = AlertManager()
        
        # Create logs directory if it doesn't exist
        self.logs_dir = Path('service_logs')
        self.logs_dir.mkdir(exist_ok=True)
        
        # UI components are initialized in show_ui
        self.root = None
        self.ui = None
        
    def show_ui(self):
        """Display the desktop UI for camera selection"""
        self.root = tk.Tk()
        self.ui = DashboardUI(self.root, self.camera_manager, self.monitor)
        self.root.mainloop()
    
    def monitor(self):
        """Main monitoring loop"""
        try:
            while True:
                # Capture image from camera
                image = self.camera_manager.capture_frame()
                if image is None:
                    print("Failed to capture frame, retrying in 5 seconds...")
                    time.sleep(5)
                    continue
                    
                # Process the image
                red_mask, green_mask, original_image = self.image_processor.process_image(image)
                
                # Extract service names from red and green regions
                down_services = self.image_processor.extract_text(original_image, red_mask)
                up_services = self.image_processor.extract_text(original_image, green_mask)
                
                # Handle each down service individually
                print(f"Found {len(down_services)} down services and {len(up_services)} up services")
                
                for service in down_services:
                    print(f"Service DOWN: {service}")
                    # Get service configuration
                    config = self.config_manager.get_service_config(service)
                    
                    # Send alerts
                    self.alert_manager.send_email_alert(service, config)
                    self.alert_manager.send_whatsapp_alert(service, config)
                
                # Log up services
                for service in up_services:
                    print(f"Service UP: {service}")
                    self.alert_manager.log_service_status(
                        service,
                        "UP",
                        False,
                        None,
                        None
                    )
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            self.camera_manager.release_camera()
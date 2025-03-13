import cv2
import numpy as np
import pytesseract
import smtplib
import os
import json
import pywhatkit
import csv
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import time
import re
from pathlib import Path

# Load environment variables
load_dotenv()

class DashboardMonitor:
    def __init__(self):
        self.camera = None  # Initialize camera later
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.email_recipients = os.getenv('EMAIL_RECIPIENTS', '').split(',')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.whatsapp_numbers = os.getenv('WHATSAPP_NUMBERS', '').split(',')
        
        # Load service-specific configurations
        self.service_configs = self._load_service_configs()
        
        # Define color thresholds for red and green in HSV
        self.red_lower = np.array([0, 120, 70])
        self.red_upper = np.array([10, 255, 255])
        self.green_lower = np.array([35, 120, 70])
        self.green_upper = np.array([85, 255, 255])

        # Create logs directory if it doesn't exist
        self.logs_dir = Path('service_logs')
        self.logs_dir.mkdir(exist_ok=True)

        # Initialize camera with user selection
        self.initialize_camera()

    def _load_service_configs(self):
        """Load and parse service-specific configurations from environment"""
        try:
            configs = os.getenv('SERVICE_CONFIGS', '{}')
            return json.loads(configs)
        except json.JSONDecodeError:
            print("Warning: Failed to parse SERVICE_CONFIGS. Using default configuration.")
            return {}

    def _get_service_config(self, service_name):
        """Get configuration for a specific service"""
        # Normalize service name for matching
        normalized_name = re.sub(r'[^a-zA-Z0-9-]', '', service_name.lower())
        
        # Try to find matching service configuration
        for config_name, config in self.service_configs.items():
            if normalized_name in config_name.lower() or config_name.lower() in normalized_name:
                return config
        
        # Return default configuration if no match found
        return {
            "email": self.email_recipients,
            "whatsapp": self.whatsapp_numbers,
            "whatsapp_groups": []
        }

    def _get_csv_filename(self):
        """Generate CSV filename based on current date"""
        return self.logs_dir / f"{datetime.now().strftime('%y_%m_%d')}.csv"

    def _ensure_csv_headers(self, filename):
        """Ensure CSV file exists with proper headers"""
        if not filename.exists():
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'Timestamp',
                    'Service Name',
                    'Status',
                    'Alert Sent',
                    'Alert Type',
                    'Recipients'
                ])

    def log_service_status(self, service_name, status, alert_sent=False, alert_type=None, recipients=None):
        """Log service status to daily CSV file"""
        csv_file = self._get_csv_filename()
        self._ensure_csv_headers(csv_file)

        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        with open(csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                service_name,
                status,
                alert_sent,
                alert_type or '',
                ', '.join(recipients) if recipients else ''
            ])

    def list_cameras(self):
        """List all available cameras and their working status"""
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

    def initialize_camera(self):
        """Initialize camera with user selection"""
        available_cameras = self.list_cameras()
        
        if not available_cameras:
            raise Exception("No cameras found!")
        
        print("\nAvailable cameras:")
        for idx, (camera_id, camera_name) in enumerate(available_cameras):
            print(f"{idx + 1}. {camera_name} (ID: {camera_id})")
        
        if len(available_cameras) == 1:
            selected_idx = 0
            print(f"\nAutomatically selected the only available camera: {available_cameras[0][1]}")
        else:
            while True:
                try:
                    selected_idx = int(input("\nSelect a camera (enter the number): ")) - 1
                    if 0 <= selected_idx < len(available_cameras):
                        break
                    print("Invalid selection. Please try again.")
                except ValueError:
                    print("Invalid input. Please enter a number.")
        
        camera_id = available_cameras[selected_idx][0]
        self.camera = cv2.VideoCapture(camera_id)
        
        if not self.camera.isOpened():
            raise Exception(f"Failed to initialize camera {camera_id}")
        
        print(f"\nSuccessfully initialized camera {available_cameras[selected_idx][1]}")

    def capture_dashboard(self):
        """Capture an image from the camera"""
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture image from camera")
        return frame

    def process_image(self, image):
        """Process the image to detect service status"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        red_mask = cv2.inRange(hsv, self.red_lower, self.red_upper)
        green_mask = cv2.inRange(hsv, self.green_lower, self.green_upper)
        return red_mask, green_mask

    def extract_text(self, image, mask):
        """Extract text near colored regions using OCR"""
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        services = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                roi = image[max(0, y-20):min(image.shape[0], y+h+20),
                          max(0, x-100):min(image.shape[1], x+w+100)]
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray_roi).strip()
                if text:
                    services.append(text)
        return services

    def send_whatsapp_alert(self, service_name, config):
        """Send WhatsApp alert for a specific service"""
        message = f"🚨 ALERT: Service Down - {service_name}\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        current_time = datetime.now()
        send_time = current_time.replace(minute=current_time.minute + 2)
        alert_sent = False
        recipients = []

        # Send to individual numbers
        for number in config.get("whatsapp", []):
            if not number.strip():
                continue
            try:
                pywhatkit.sendwhatmsg(
                    number.strip(),
                    message,
                    send_time.hour,
                    send_time.minute,
                    wait_time=15,
                    tab_close=True
                )
                print(f"WhatsApp alert sent to {number} for service {service_name}")
                alert_sent = True
                recipients.append(number)
            except Exception as e:
                print(f"Failed to send WhatsApp alert to {number}: {str(e)}")

        # Send to group chats
        for group_link in config.get("whatsapp_groups", []):
            try:
                group_id = group_link.split('/')[-1]
                pywhatkit.sendwhatmsg_to_group(
                    group_id,
                    message,
                    send_time.hour,
                    send_time.minute,
                    wait_time=15,
                    tab_close=True
                )
                print(f"WhatsApp alert sent to group {group_id} for service {service_name}")
                alert_sent = True
                recipients.append(f"group:{group_id}")
            except Exception as e:
                print(f"Failed to send WhatsApp alert to group {group_link}: {str(e)}")

        # Log WhatsApp alert status
        self.log_service_status(
            service_name,
            "DOWN",
            alert_sent,
            "WhatsApp",
            recipients
        )

    def send_email_alert(self, service_name, config):
        """Send email alert for a specific service"""
        if not self.email_sender or not self.email_password:
            return

        recipients = config.get("email", self.email_recipients)
        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = f"ALERT: Service Down - {service_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = f"The service {service_name} is currently DOWN.\n"
        body += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))

        alert_sent = False
        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
                print(f"Email alert sent successfully for service {service_name}")
                alert_sent = True
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")

        # Log email alert status
        self.log_service_status(
            service_name,
            "DOWN",
            alert_sent,
            "Email",
            recipients
        )

    def monitor(self):
        """Main monitoring loop"""
        try:
            while True:
                image = self.capture_dashboard()
                red_mask, green_mask = self.process_image(image)
                
                down_services = self.extract_text(image, red_mask)
                up_services = self.extract_text(image, green_mask)
                
                # Log all service statuses
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Handle each down service individually
                for service in down_services:
                    print(f"Service DOWN: {service}")
                    config = self._get_service_config(service)
                    self.send_email_alert(service, config)
                    self.send_whatsapp_alert(service, config)
                
                # Log up services
                for service in up_services:
                    print(f"Service UP: {service}")
                    self.log_service_status(
                        service,
                        "UP",
                        False,
                        None,
                        None
                    )
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            self.camera.release()

if __name__ == "__main__":
    monitor = DashboardMonitor()
    monitor.monitor()
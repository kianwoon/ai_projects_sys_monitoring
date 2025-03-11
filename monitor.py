import cv2
import numpy as np
import pytesseract
import smtplib
import os
import json
import pywhatkit
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import time
import re

# Load environment variables
load_dotenv()

class DashboardMonitor:
    def __init__(self):
        self.camera = cv2.VideoCapture(0)  # Use default camera
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
            except Exception as e:
                print(f"Failed to send WhatsApp alert to {number}: {str(e)}")

        # Send to group chats
        for group_link in config.get("whatsapp_groups", []):
            try:
                # Extract group ID from the invite link
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
            except Exception as e:
                print(f"Failed to send WhatsApp alert to group {group_link}: {str(e)}")

    def send_email_alert(self, service_name, config):
        """Send email alert for a specific service"""
        if not self.email_sender or not self.email_password:
            return

        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = ', '.join(config.get("email", self.email_recipients))
        msg['Subject'] = f"ALERT: Service Down - {service_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = f"The service {service_name} is currently DOWN.\n"
        body += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
                print(f"Email alert sent successfully for service {service_name}")
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")

    def monitor(self):
        """Main monitoring loop"""
        try:
            while True:
                image = self.capture_dashboard()
                red_mask, green_mask = self.process_image(image)
                
                down_services = self.extract_text(image, red_mask)
                up_services = self.extract_text(image, green_mask)
                
                # Handle each down service individually
                for service in down_services:
                    print(f"Service DOWN: {service}")
                    config = self._get_service_config(service)
                    self.send_email_alert(service, config)
                    self.send_whatsapp_alert(service, config)
                
                if up_services:
                    print(f"Services UP: {up_services}")
                
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            self.camera.release()

if __name__ == "__main__":
    monitor = DashboardMonitor()
    monitor.monitor() 
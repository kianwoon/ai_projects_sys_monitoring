import cv2
import numpy as np
import pytesseract
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import time

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
        
        # Define color thresholds for red and green in HSV
        self.red_lower = np.array([0, 120, 70])
        self.red_upper = np.array([10, 255, 255])
        self.green_lower = np.array([35, 120, 70])
        self.green_upper = np.array([85, 255, 255])

    def capture_dashboard(self):
        """Capture an image from the camera"""
        ret, frame = self.camera.read()
        if not ret:
            raise Exception("Failed to capture image from camera")
        return frame

    def process_image(self, image):
        """Process the image to detect service status"""
        # Convert to HSV color space
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Create masks for red and green colors
        red_mask = cv2.inRange(hsv, self.red_lower, self.red_upper)
        green_mask = cv2.inRange(hsv, self.green_lower, self.green_upper)
        
        return red_mask, green_mask

    def extract_text(self, image, mask):
        """Extract text near colored regions using OCR"""
        # Find contours in the mask
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        services = []
        for contour in contours:
            if cv2.contourArea(contour) > 100:  # Filter small noise
                x, y, w, h = cv2.boundingRect(contour)
                # Expand ROI to include surrounding text
                roi = image[max(0, y-20):min(image.shape[0], y+h+20),
                          max(0, x-100):min(image.shape[1], x+w+100)]
                
                # Convert ROI to grayscale for OCR
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray_roi).strip()
                if text:
                    services.append(text)
        
        return services

    def send_alert(self, down_services):
        """Send email alert for down services"""
        if not down_services or not self.email_sender or not self.email_password:
            return

        msg = MIMEMultipart()
        msg['From'] = self.email_sender
        msg['To'] = ', '.join(self.email_recipients)
        msg['Subject'] = f"ALERT: Services Down - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        body = "The following services are currently DOWN:\n\n"
        body += "\n".join([f"- {service}" for service in down_services])
        msg.attach(MIMEText(body, 'plain'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email_sender, self.email_password)
                server.send_message(msg)
        except Exception as e:
            print(f"Failed to send email alert: {str(e)}")

    def monitor(self):
        """Main monitoring loop"""
        try:
            while True:
                # Capture and process dashboard image
                image = self.capture_dashboard()
                red_mask, green_mask = self.process_image(image)
                
                # Extract service names from regions
                down_services = self.extract_text(image, red_mask)
                up_services = self.extract_text(image, green_mask)
                
                # Send alert if any services are down
                if down_services:
                    print(f"Services DOWN: {down_services}")
                    self.send_alert(down_services)
                
                print(f"Services UP: {up_services}")
                
                # Wait before next check
                time.sleep(60)  # Check every minute
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
        finally:
            self.camera.release()

if __name__ == "__main__":
    monitor = DashboardMonitor()
    monitor.monitor() 
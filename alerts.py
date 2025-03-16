"""
Alert sending functionality for the service monitor
"""
import os
import smtplib
import pywhatkit
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

class AlertManager:
    """Manages sending alerts when services are down"""
    
    def __init__(self):
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Create logs directory if it doesn't exist
        self.logs_dir = Path('service_logs')
        self.logs_dir.mkdir(exist_ok=True)
    
    def send_whatsapp_alert(self, service_name, config):
        """
        Send WhatsApp alert for a specific service
        
        Args:
            service_name (str): Name of the service
            config (dict): Service configuration
            
        Returns:
            bool: True if alert was sent successfully
        """
        message = f"🔴 ALERT: Service Down - {service_name}\n"
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
        
        return alert_sent

    def send_email_alert(self, service_name, config):
        """
        Send email alert for a specific service
        
        Args:
            service_name (str): Name of the service
            config (dict): Service configuration
            
        Returns:
            bool: True if alert was sent successfully
        """
        if not self.email_sender or not self.email_password:
            print("Email credentials not configured")
            return False

        recipients = config.get("email", [])
        if not recipients:
            print("No email recipients configured")
            return False
            
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
        
        return alert_sent
        
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
        """
        Log service status to daily CSV file
        
        Args:
            service_name (str): Name of the service
            status (str): Service status (UP/DOWN)
            alert_sent (bool): Whether alert was sent
            alert_type (str): Type of alert sent
            recipients (list): List of alert recipients
        """
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
            
        print(f"Logged {status} status for {service_name}")
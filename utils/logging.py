"""
Logging utilities for the service monitor application
"""
import csv
from datetime import datetime
from pathlib import Path

class ServiceLogger:
    """Logger for service monitoring activities"""
    
    def __init__(self, log_dir='service_logs'):
        """
        Initialize the logger
        
        Args:
            log_dir (str): Directory to store log files
        """
        self.logs_dir = Path(log_dir)
        self.logs_dir.mkdir(exist_ok=True)
    
    def get_log_filename(self):
        """
        Generate log filename based on current date
        
        Returns:
            Path: Log file path
        """
        return self.logs_dir / f"{datetime.now().strftime('%y_%m_%d')}.csv"
    
    def ensure_log_headers(self, filename):
        """
        Ensure log file exists with proper headers
        
        Args:
            filename (Path): Log file path
        """
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
        csv_file = self.get_log_filename()
        self.ensure_log_headers(csv_file)

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
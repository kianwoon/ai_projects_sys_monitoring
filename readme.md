# Grafana Dashboard Monitor

This application monitors a Grafana dashboard through your computer's camera and sends email and WhatsApp alerts when services are detected as down. It uses computer vision and OCR to detect service status based on color indicators (red for down, green for up).

## Prerequisites

1. Python 3.13.2 or higher
2. Tesseract OCR engine installed on your system
3. A webcam or camera connected to your computer
4. SMTP access for sending email alerts (e.g., Gmail account)
5. WhatsApp Web access for sending WhatsApp messages

## Installation

1. Install Tesseract OCR:
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt-get install tesseract-ocr`
   - Windows: Download installer from https://github.com/UB-Mannheim/tesseract/wiki

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Copy `.env.example` to `.env`
   - Update the following variables in `.env`:
     - `EMAIL_SENDER`: Your email address
     - `EMAIL_PASSWORD`: Your email app password (for Gmail, create an App Password)
     - `EMAIL_RECIPIENTS`: Default list of email recipients
     - `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
     - `SMTP_PORT`: SMTP port (default: 587)
     - `WHATSAPP_NUMBERS`: Default list of WhatsApp numbers
     - `SERVICE_CONFIGS`: JSON configuration for service-specific notifications

### Service-Specific Configuration

The `SERVICE_CONFIGS` in `.env` allows you to define different notification targets for different services. Example configuration:

```json
SERVICE_CONFIGS={
    "database": {
        "email": ["db-team@company.com", "dba@company.com"],
        "whatsapp": ["+1234567890"],
        "whatsapp_groups": ["https://chat.whatsapp.com/db-team"]
    },
    "api-gateway": {
        "email": ["api-team@company.com"],
        "whatsapp": ["+0987654321"],
        "whatsapp_groups": ["https://chat.whatsapp.com/api-team"]
    }
}
```

Each service configuration includes:
- `email`: List of email addresses for this service
- `whatsapp`: List of WhatsApp numbers for individual messages
- `whatsapp_groups`: List of WhatsApp group chat invite links

If a service name is not found in the configuration, the system will use the default recipients.

### Service Status Logging

The application automatically logs all service status changes and alert attempts to daily CSV files in the `service_logs` directory. The files are named in the format `YY_MM_DD.csv` (e.g., `23_03_15.csv` for March 15, 2023).

Each log entry contains:
- Timestamp: Date and time of the status check
- Service Name: Name of the monitored service
- Status: Current status (UP/DOWN)
- Alert Sent: Whether an alert was successfully sent
- Alert Type: Type of alert (Email/WhatsApp)
- Recipients: List of recipients who received the alert

Example log entry:
```csv
Timestamp,Service Name,Status,Alert Sent,Alert Type,Recipients
2023-03-15 14:30:45,database,DOWN,True,Email,db-team@company.com,dba@company.com
2023-03-15 14:30:46,database,DOWN,True,WhatsApp,+1234567890,group:db-team
2023-03-15 14:31:45,api-gateway,UP,False,,
```

## Service Management UI

The service management UI has been enhanced to improve usability and functionality. The following changes have been made:

### Treeview Layout
- The services are now displayed in a grid format using a `ttk.Treeview`.
- The columns include:
  - **Service Name**: The name of the service.
  - **Email**: Email addresses associated with the service.
  - **WhatsApp**: WhatsApp numbers for notifications.
  - **WhatsApp Groups**: Groups for WhatsApp notifications.

### Adding and Managing Services
- Users can add new services using the `+ New Service` button.
- The `Default Configuration` button allows users to load predefined settings for alerts.
- Upon selecting a service from the grid, users can edit its details.

### Example Configuration
- The configuration for services is stored in a JSON format, which includes email and WhatsApp settings.
- Ensure that the `service_config.json` file is updated accordingly to reflect any changes made in the UI.

### Usage Instructions
- To run the application, use the command: `python3 monitor.py`
- Ensure all dependencies are installed as specified in `requirements.txt`.

For further details on the configuration, refer to the `service_config.json` file.

## Usage

1. Position your camera to capture the Grafana dashboard clearly
2. Ensure you're logged into WhatsApp Web in your default browser
3. Run the monitoring script:
   ```bash
   python3 monitor.py
   ```

4. The script will:
   - Capture dashboard images every minute
   - Process the image to detect service status
   - Send targeted notifications to service-specific teams when services are down
   - Log all status changes and alert attempts to daily CSV files
   - Print status updates to the console

Press Ctrl+C to stop monitoring.

## How it Works

1. **Image Capture**: Uses OpenCV to capture images from your camera
2. **Color Detection**: Processes images in HSV color space to detect red (down) and green (up) indicators
3. **Text Extraction**: Uses Tesseract OCR to extract service names from regions around color indicators
4. **Smart Notification System**: 
   - Matches detected service names with configured teams
   - Sends email alerts via SMTP to service-specific teams
   - Sends WhatsApp messages to individual numbers and group chats
   - Falls back to default recipients if no specific configuration is found
5. **Status Logging**:
   - Creates daily CSV files for status tracking
   - Records all service statuses and alert attempts
   - Maintains history of service availability
   - Enables analysis of service reliability and alert effectiveness

## Troubleshooting

1. **Camera Access**: Ensure your camera is properly connected and accessible
2. **OCR Quality**: Adjust camera position and focus for clear text capture
3. **Email Alerts**: For Gmail, use App Passwords if 2FA is enabled
4. **Color Detection**: Adjust HSV thresholds in code if needed for your specific dashboard
5. **WhatsApp Alerts**:
   - Make sure you're logged into WhatsApp Web in your default browser
   - The first time you run the script, you may need to scan the QR code
   - If messages aren't sending, try increasing the `wait_time` parameter in the code
6. **Service Matching**:
   - Service names are matched case-insensitively
   - Special characters are removed for matching
   - If a service doesn't match any configuration, default recipients are used
7. **Logging Issues**:
   - Check write permissions in the `service_logs` directory
   - Ensure sufficient disk space for log files
   - CSV files can be opened in Excel or any spreadsheet software for analysis

## License

MIT License
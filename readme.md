# Grafana Dashboard Monitor

This application monitors a Grafana dashboard through your computer's camera and sends email alerts when services are detected as down. It uses computer vision and OCR to detect service status based on color indicators (red for down, green for up).

## Prerequisites

1. Python 3.7 or higher
2. Tesseract OCR engine installed on your system
3. A webcam or camera connected to your computer
4. SMTP access for sending email alerts (e.g., Gmail account)

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
     - `EMAIL_RECIPIENTS`: Comma-separated list of recipients
     - `SMTP_SERVER`: SMTP server (default: smtp.gmail.com)
     - `SMTP_PORT`: SMTP port (default: 587)

## Usage

1. Position your camera to capture the Grafana dashboard clearly
2. Run the monitoring script:
   ```bash
   python monitor.py
   ```

3. The script will:
   - Capture dashboard images every minute
   - Process the image to detect service status
   - Send email alerts when services are detected as down
   - Print status updates to the console

Press Ctrl+C to stop monitoring.

## How it Works

1. **Image Capture**: Uses OpenCV to capture images from your camera
2. **Color Detection**: Processes images in HSV color space to detect red (down) and green (up) indicators
3. **Text Extraction**: Uses Tesseract OCR to extract service names from regions around color indicators
4. **Alert System**: Sends email alerts via SMTP when services are detected as down

## Troubleshooting

1. **Camera Access**: Ensure your camera is properly connected and accessible
2. **OCR Quality**: Adjust camera position and focus for clear text capture
3. **Email Alerts**: For Gmail, use App Passwords if 2FA is enabled
4. **Color Detection**: Adjust HSV thresholds in code if needed for your specific dashboard

## License

MIT License
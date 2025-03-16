"""
Image processing utilities for service monitoring
"""
import cv2
import numpy as np
import pytesseract
from pathlib import Path
import os

class ImageProcessor:
    """Handles processing camera images to detect service status indicators"""
    
    def __init__(self):
        # Define color thresholds for red and green in HSV
        self.red_lower = np.array([0, 120, 70])
        self.red_upper = np.array([10, 255, 255])
        self.green_lower = np.array([35, 120, 70])
        self.green_upper = np.array([85, 255, 255])
        self.orange_lower = np.array([10, 100, 100])
        self.orange_upper = np.array([25, 255, 255])
    
    def process_image(self, image):
        """
        Process the image to detect service status
        
        Args:
            image: OpenCV image object
            
        Returns:
            tuple: (red_mask, green_mask)
        """
        if image is None:
            raise ValueError("Image cannot be None")
            
        # Make a copy of the original image
        original_image = image.copy()
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
        
        # Create masks for red and green
        red_mask = cv2.inRange(hsv, self.red_lower, self.red_upper)
        green_mask = cv2.inRange(hsv, self.green_lower, self.green_upper)
        
        # Save for debugging if needed
        output_path = Path("dashboard_screenshot.jpg")
        cv2.imwrite(str(output_path), original_image)
        
        return red_mask, green_mask, original_image
    
    def detect_services(self, image):
        """
        Detect service circles and extract service names
        
        Args:
            image: OpenCV image object
            
        Returns:
            list: List of detected service names
        """
        # Make a copy of the original image
        original_image = image.copy()
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(original_image, cv2.COLOR_BGR2HSV)
        
        # Create mask for orange (service circles)
        mask_orange = cv2.inRange(hsv, self.orange_lower, self.orange_upper)
        
        # Find contours
        contours, _ = cv2.findContours(mask_orange, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process each contour
        detected_services = []
        annotated_img = original_image.copy()
        
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < 50:  # Filter out small noise
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            aspect_ratio = float(w) / h
            if 0.9 <= aspect_ratio <= 1.1:  # Circles have aspect ratio close to 1
                # Expand the rectangle for text detection
                rectangle_width = int(w * 1.4)
                rectangle_height = int(h * 2)

                # Center horizontally around the circle
                x1 = x + (w // 2) - (rectangle_width // 2)
                y1 = y

                # Bottom-right corner
                x2 = x1 + rectangle_width
                y2 = y1 + rectangle_height

                # Ensure coordinates are within image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(original_image.shape[1], x2)
                y2 = min(original_image.shape[0], y2)

                # Draw the expanded rectangle
                cv2.rectangle(annotated_img, (x1, y1), (x2, y2), (255, 0, 0), thickness=3)

                # Extract and process the ROI
                cropped_image = original_image[y1:y2, x1:x2]
                
                # Save cropped image for debugging
                cv2.imwrite('cropped_roi.jpeg', cropped_image)
                
                # Convert to grayscale for OCR
                gray_cropped_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)

                # Apply Otsu's thresholding
                _, thresh_image = cv2.threshold(gray_cropped_image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

                # OCR to extract text
                custom_config = r'--oem 3 --psm 6'
                extracted_text = pytesseract.image_to_string(
                    thresh_image, config=custom_config
                ).strip()

                # Clean up text
                if '\n' in extracted_text:
                    extracted_text = ' '.join(extracted_text.splitlines())

                service_name = extracted_text.strip() if extracted_text else ''
                if service_name:
                    detected_services.append(service_name)

        # Save annotated image
        cv2.imwrite('annotated_img.jpeg', annotated_img)
        
        return detected_services, annotated_img

    def extract_text(self, image, mask):
        """
        Extract text near colored regions using OCR
        
        Args:
            image: OpenCV image object
            mask: Binary mask of regions of interest
            
        Returns:
            list: List of extracted service names
        """
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        services = []
        
        for contour in contours:
            if cv2.contourArea(contour) > 100:
                x, y, w, h = cv2.boundingRect(contour)
                roi = image[max(0, y-20):min(image.shape[0], y+h+20),
                          max(0, x-100):min(image.shape[1], x+w+100)]
                
                if roi.size == 0:  # Skip empty ROIs
                    continue
                    
                gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
                text = pytesseract.image_to_string(gray_roi).strip()
                if text:
                    services.append(text)
                    
        return services
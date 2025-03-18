import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import cv2
from monitor import DashboardMonitor
import threading
import queue
import time

class ServiceGrid(ttk.Frame):
    """Grid display for service status indicators"""
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configure grid layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.canvas = tk.Canvas(self, bg='gray95')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        # Configure canvas
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Grid layout
        self.canvas.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Initialize services grid
        self.services = {}
        self.create_sample_grid()
        
    def create_sample_grid(self):
        """Create a sample grid layout similar to the dashboard"""
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create section frames
        sections = {
            'Internet WAS': {'row': 0, 'col': 0},
            'IVR': {'row': 1, 'col': 0},
            'ITD Payment': {'row': 2, 'col': 0}
        }
        
        for name, pos in sections.items():
            frame = ttk.LabelFrame(self.scrollable_frame, text=name, padding=10)
            frame.grid(row=pos['row'], column=pos['col'], sticky='nsew', padx=5, pady=5)
            
            # Add some sample services to each section
            if name == 'Internet WAS':
                services = [
                    ('BTSS', 'Cyber Channel'),
                    ('CHSS_EJB', 'EBanking'),
                    ('CHSS_Internet', 'EBanking'),
                    ('ECIS', 'Loans'),
                    ('IVSS_ejb', 'WMS'),
                    ('IWPG_Internet', 'EBanking')
                ]
            elif name == 'IVR':
                services = [
                    ('IVR1', 'Health'),
                    ('IVR2', 'Status'),
                    ('IVR3', 'Payments')
                ]
            else:  # ITD Payment
                services = [
                    ('Payment1', 'Processing'),
                    ('Payment2', 'Validation'),
                    ('Payment3', 'Settlement')
                ]
            
            # Create service indicators
            for i, (service, desc) in enumerate(services):
                service_frame = ttk.Frame(frame)
                service_frame.grid(row=i//3, column=i%3, padx=5, pady=5)
                
                # Service indicator (circle)
                canvas = tk.Canvas(service_frame, width=20, height=20, 
                                 highlightthickness=0, bg='gray95')
                canvas.create_oval(2, 2, 18, 18, fill='gray80', outline='gray70')
                canvas.grid(row=0, column=0, padx=(0,5))
                
                # Service name and description
                ttk.Label(service_frame, text=f"{service}\n({desc})", 
                         justify=tk.LEFT, style='Small.TLabel').grid(row=0, column=1)
                
                # Store reference
                self.services[service] = canvas

class MonitoringGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Service Monitoring System")
        self.root.geometry("1200x900")
        
        # Configure style
        style = ttk.Style()
        style.configure('Header.TLabel', font=('Helvetica', 10, 'bold'))
        style.configure('Status.TLabel', font=('Helvetica', 9))
        style.configure('Small.TLabel', font=('Helvetica', 8))
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky="nsew")
        
        # Camera Selection Section
        self.create_camera_section()
        
        # Service Grid Section
        self.service_grid = ServiceGrid(self.main_frame)
        self.service_grid.grid(row=1, column=0, sticky="nsew", pady=10)
        
        # Control Buttons Section
        self.create_control_section()
        
        # Status Bar
        self.status_bar = ttk.Label(self.main_frame, text="Status: One camera detected (auto-selected)", 
                                  relief=tk.SUNKEN, padding=(5, 2))
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(5,0))
        
        # Initialize monitoring
        self.monitor = DashboardMonitor()
        self.is_monitoring = False
        self.update_queue = queue.Queue()
        
        # Configure grid weights
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)
        
    def create_camera_section(self):
        """Create camera selection section"""
        camera_frame = ttk.LabelFrame(self.main_frame, text="Camera Selection", padding="5")
        camera_frame.grid(row=0, column=0, sticky="ew", pady=(0,5))
        
        # Camera Selection Frame
        select_frame = ttk.Frame(camera_frame)
        select_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=5)
        
        # Camera Dropdown
        self.camera_var = tk.StringVar(value="Camera 1 (ID: 1)")
        self.camera_dropdown = ttk.Combobox(select_frame, textvariable=self.camera_var, width=50)
        self.camera_dropdown['values'] = ['Camera 1 (ID: 1)']
        self.camera_dropdown.grid(row=0, column=0, sticky="ew", padx=(5,5))
        
        # Refresh Button
        self.refresh_btn = ttk.Button(select_frame, text="Refresh", 
                                    command=self.refresh_cameras, width=15)
        self.refresh_btn.grid(row=0, column=1, padx=5)
        
        # Start Button
        self.start_btn = ttk.Button(select_frame, text="Start Monitoring", 
                                  command=self.start_monitoring, width=15)
        self.start_btn.grid(row=0, column=2, padx=5)
        
        select_frame.grid_columnconfigure(0, weight=1)
        
    def create_control_section(self):
        """Create control buttons section"""
        button_frame = ttk.Frame(self.main_frame)
        button_frame.grid(row=2, column=0, sticky="e", pady=5)
        
        # Process Image Button
        self.process_btn = ttk.Button(button_frame, text="Process Image", 
                                    command=self.process_image, width=15)
        self.process_btn.grid(row=0, column=0, padx=5)
        
        # Alert Configuration Button
        self.alert_btn = ttk.Button(button_frame, text="Alert Configuration", 
                                  command=self.configure_alerts, width=15)
        self.alert_btn.grid(row=0, column=1, padx=5)
        
    def refresh_cameras(self):
        """Refresh available cameras"""
        self.status_bar.config(text="Status: Refreshing camera list...")
        self.status_bar.config(text="Status: One camera detected (auto-selected)")
        
    def start_monitoring(self):
        """Start/Stop monitoring"""
        if not self.is_monitoring:
            self.is_monitoring = True
            self.start_btn.config(text="Stop Monitoring")
            self.monitoring_thread = threading.Thread(target=self.monitor_loop)
            self.monitoring_thread.daemon = True
            self.monitoring_thread.start()
            self.status_bar.config(text="Status: Monitoring started")
        else:
            self.is_monitoring = False
            self.start_btn.config(text="Start Monitoring")
            self.status_bar.config(text="Status: Monitoring stopped")
            
    def monitor_loop(self):
        """Main monitoring loop"""
        while self.is_monitoring:
            try:
                frame = self.monitor.capture_frame()
                if frame is not None:
                    services, annotated = self.monitor.process_frame(frame)
                    self.update_service_status(services)
            except Exception as e:
                print(f"Error in monitoring loop: {str(e)}")
                self.status_bar.config(text=f"Status: Error - {str(e)}")
            time.sleep(1)
            
    def update_service_status(self, active_services):
        """Update service status indicators"""
        for service, canvas in self.service_grid.services.items():
            # Update circle color based on service status
            if service in active_services:
                canvas.create_oval(2, 2, 18, 18, fill='#90EE90', outline='#228B22')  # Green
            else:
                canvas.create_oval(2, 2, 18, 18, fill='gray80', outline='gray70')  # Gray
            
    def process_image(self):
        """Process current frame"""
        try:
            self.status_bar.config(text="Status: Processing image...")
            frame = self.monitor.capture_frame()
            if frame is not None:
                services, _ = self.monitor.process_frame(frame)
                self.update_service_status(services)
                self.status_bar.config(text="Status: Image processed successfully")
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            self.status_bar.config(text=f"Status: Error processing image - {str(e)}")
            
    def configure_alerts(self):
        """Open alert configuration window"""
        alert_window = tk.Toplevel(self.root)
        alert_window.title("Alert Configuration")
        alert_window.geometry("400x300")
        
        ttk.Label(alert_window, text="Alert Configuration", 
                 style='Header.TLabel').pack(pady=10)
        ttk.Label(alert_window, text="Configuration options will be added here", 
                 style='Status.TLabel').pack(pady=10)

def main():
    root = tk.Tk()
    app = MonitoringGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()

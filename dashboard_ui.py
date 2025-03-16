"""
Dashboard UI components for the main monitoring interface
"""
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
import re

from alert_config_ui import AlertConfigUI
from ui_utils import CreateToolTip

class DashboardUI:
    """UI components for the main monitoring dashboard"""
    
    def __init__(self, root, camera_manager, on_start_callback):
        """
        Initialize the dashboard UI
        
        Args:
            root: Tkinter root window
            camera_manager: CameraManager instance
            on_start_callback: Callback function when monitoring starts
        """
        self.root = root
        self.camera_manager = camera_manager
        self.on_start_callback = on_start_callback
        self.camera_var = None
        self.service_display = None
        self.image_label = None
        
        self._setup_root()
        self._create_menu()
        self._create_main_ui()
    
    def _setup_root(self):
        """Configure the root window"""
        self.root.title("Service Monitoring System")
        self.root.geometry('1500x1300')  # Set the main application window size
        self.root.minsize(1500, 1300)    # Minimum size
        self.root.configure(bg='#F0F0F0')
        
        # Set styles
        style = ttk.Style()
        style.theme_use('clam')  # Use clam theme as base
        style.configure('TFrame', background='#F0F0F0')
        style.configure('TButton', padding=6, relief="raised")
        style.configure('TLabel', background='#F0F0F0', foreground='#000000')
        style.configure('TLabelframe', background='#F0F0F0')
        style.configure('TLabelframe.Label', background='#F0F0F0', foreground='#000000', font=('Segoe UI', 9, 'bold'))
        style.configure('TSeparator', background='#C0C0C0')
        style.configure('TNotebook', background='#F0F0F0')
        style.configure('TNotebook.Tab', padding=[10, 4], font=('Segoe UI', 9), background='#E1E1E1')
        style.configure('TEntry', fieldbackground='white', foreground='black')
        style.configure('TCombobox', fieldbackground='white', foreground='black')
        style.map('TNotebook.Tab', background=[('selected', '#F0F0F0'), ('active', '#E5E5E5')])
        
        # Make sure all child widgets inherit these styles
        self.root.option_add("*TCombobox*Listbox*Background", 'white')
        self.root.option_add("*TCombobox*Listbox*Foreground", 'black')
        self.root.option_add("*Background", '#F0F0F0')
        self.root.option_add("*Foreground", 'black')
    
    def _create_menu(self):
        """Create menu bar"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Start Monitoring", command=self.start_monitoring)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Configuration menu
        config_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Configuration", menu=config_menu)
        config_menu.add_command(label="Alert Settings", command=lambda: AlertConfigUI(self.root))
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
    
    def _create_main_ui(self):
        """Create the main UI components"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Notebook (tabbed interface)
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Camera tab
        camera_tab = ttk.Frame(notebook)
        notebook.add(camera_tab, text="Camera Selection")
        
        # Status bar
        status_frame = ttk.Frame(self.root, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Ready", padding=(10, 3))
        self.status_label.pack(side=tk.LEFT)
        
        # Camera selection frame
        camera_frame = ttk.LabelFrame(camera_tab, text="Available Cameras")
        camera_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera list frame
        camera_list_frame = ttk.Frame(camera_frame)
        camera_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Camera dropdown with label
        camera_label_frame = ttk.Frame(camera_list_frame)
        camera_label_frame.pack(fill=tk.X, pady=(0, 5))
        ttk.Label(camera_label_frame, text="Select Camera:").pack(side=tk.LEFT)
        
        # Camera dropdown and re-detect in same row
        camera_control_frame = ttk.Frame(camera_list_frame)
        camera_control_frame.pack(fill=tk.X, pady=5)
        
        self.camera_var = tk.StringVar()
        camera_dropdown = ttk.Combobox(camera_control_frame, textvariable=self.camera_var, 
                                    state='readonly', width=50)
        camera_dropdown.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Start button for reference
        start_btn = ttk.Button(
            camera_list_frame, 
            text="Start Monitoring", 
            width=20,
            command=self.start_monitoring
        )
        
        redetect_btn = ttk.Button(camera_control_frame, text="Refresh", width=15,
                                command=lambda: self.update_camera_list(camera_dropdown, start_btn))
        redetect_btn.pack(side=tk.RIGHT)
        
        # Separator
        ttk.Separator(camera_list_frame, orient='horizontal').pack(fill=tk.X, pady=15)
        
        # Information frame
        info_frame = ttk.Frame(camera_list_frame)
        info_frame.pack(fill=tk.X, pady=5)
        
        # Camera info
        self.camera_info = ttk.Label(info_frame, text="No camera selected")
        self.camera_info.pack(anchor=tk.W)
        
        # Action buttons frame
        button_frame = ttk.Frame(camera_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Action buttons
        start_btn.pack(side=tk.RIGHT, padx=5)
        
        config_btn = ttk.Button(button_frame, text="Alert Configuration", width=20,
                              command=lambda: AlertConfigUI(self.root))
        config_btn.pack(side=tk.RIGHT, padx=5)
        
        process_image_button = ttk.Button(button_frame, text="Process Image", width=20,
                              command=self.process_image)
        process_image_button.pack(side=tk.RIGHT, padx=5)
        
        # Create a frame to hold both the image and the service display side by side
        side_by_side_frame = tk.Frame(camera_tab)
        side_by_side_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Image preview on the left
        self.image_label = ttk.Label(side_by_side_frame)
        self.image_label.pack(side=tk.LEFT, padx=10, pady=10)

        # Add a section to display detected service names on the right
        self.service_display = tk.Text(side_by_side_frame, height=10, width=30, font=('Helvetica', 14))
        self.service_display.pack(side=tk.RIGHT, padx=10)
        self.service_display.insert(tk.END, 'Detected Services:\n')
        self.service_display.config(state=tk.DISABLED)  # Disable editing until image is processed
        self.service_display.pack_forget()  # Hide the section until image processing

        # Initial camera detection
        self.update_camera_list(camera_dropdown, start_btn)
        
        # Center window
        self.center_window()
    
    def update_camera_list(self, camera_dropdown, start_btn):
        """
        Update the camera dropdown list and monitoring button state
        
        Args:
            camera_dropdown: Combobox for camera selection
            start_btn: Start monitoring button
        """
        available_cameras = self.camera_manager.list_cameras()
        
        if not available_cameras:
            camera_dropdown['values'] = ['No cameras detected']
            camera_dropdown.set('No cameras detected')
            camera_dropdown.state(['readonly'])
            start_btn.state(['disabled'])
            self.status_label.configure(text="Status: No cameras detected")
            self.camera_info.configure(text="Please connect a camera to use the monitoring system")
        else:
            camera_names = [f"{camera_name} (ID: {camera_id})" for camera_id, camera_name in available_cameras]
            camera_dropdown['values'] = camera_names
            
            if len(available_cameras) == 1:
                camera_dropdown.set(camera_names[0])
                self.status_label.configure(text="Status: One camera detected (auto-selected)")
                self.camera_info.configure(text=f"Using camera: {available_cameras[0][1]}")
            else:
                camera_dropdown.set(camera_names[0])
                self.status_label.configure(text=f"Status: {len(available_cameras)} cameras available")
                self.camera_info.configure(text=f"Selected camera: {available_cameras[0][1]}")
            
            camera_dropdown.state(['readonly'])
            start_btn.state(['!disabled'])
    
    def start_monitoring(self):
        """Start monitoring with selected camera"""
        if not self.camera_var:
            return
            
        selected_camera = self.camera_var.get()
        if selected_camera == 'No cameras detected':
            messagebox.showerror("Error", "No camera available for monitoring")
            return
            
        # Initialize the selected camera
        match = re.search(r'ID: (\d+)', selected_camera)
        if not match:
            messagebox.showerror("Error", "Invalid camera selection")
            return
            
        camera_id = int(match.group(1))
        if not self.camera_manager.initialize_camera(camera_id):
            messagebox.showerror("Error", f"Failed to initialize camera {camera_id}")
            return
            
        # Call the callback function to start monitoring
        self.root.destroy()
        self.on_start_callback()
    
    def process_image(self):
        """Process a test image instead of capturing from camera"""
        from image_processor import ImageProcessor
        
        processor = ImageProcessor()
        
        # Load a test image
        test_image_path = 'img/test.jpeg'
        try:
            image = cv2.imread(test_image_path)
            if image is None:
                messagebox.showerror('Error', 'Failed to load test image. Please check the file path.')
                return
        except Exception as e:
            messagebox.showerror('Error', f'Error loading test image: {str(e)}')
            return
            
        # Process the image
        services, annotated_img = processor.detect_services(image)
        
        # Display the annotated image
        annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)
        annotated_img = Image.fromarray(annotated_img)
        annotated_img = annotated_img.resize((1024, 576), Image.LANCZOS)  # Use LANCZOS for resizing
        annotated_img = ImageTk.PhotoImage(annotated_img)
        self.image_label.config(image=annotated_img)
        self.image_label.image = annotated_img  # Keep a reference to avoid garbage collection
        
        # Display detected services
        if services:
            self.service_display.pack(side=tk.RIGHT, padx=10)  # Show the section
            self.service_display.config(state=tk.NORMAL)  # Enable editing
            self.service_display.delete(1.0, tk.END)
            self.service_display.insert(tk.END, f'Detected Services ({len(services)} total):\n')
            for service in services:
                self.service_display.insert(tk.END, f'- {service}\n')
            self.service_display.config(state=tk.DISABLED)  # Disable editing again
    
    def show_about(self):
        """Show about dialog"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About Service Monitoring System")
        about_window.geometry("400x200")
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the window
        about_window.update_idletasks()
        width = about_window.winfo_width()
        height = about_window.winfo_height()
        x = (about_window.winfo_screenwidth() // 2) - (width // 2)
        y = (about_window.winfo_screenheight() // 2) - (height // 2)
        about_window.geometry(f'+{x}+{y}')
        
        # Content
        frame = ttk.Frame(about_window, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Service Monitoring System", 
                font=('Segoe UI', 12, 'bold')).pack(pady=(0, 10))
        ttk.Label(frame, text="Version 1.1").pack()
        ttk.Label(frame, text="© 2025 All Rights Reserved").pack(pady=(10, 0))
        
        ttk.Button(frame, text="OK", command=about_window.destroy, width=10).pack(pady=20)
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.root.geometry(f'+{x}+{y}')
        print('Main screen dimensions:', self.root.winfo_width(), 'x', self.root.winfo_height())
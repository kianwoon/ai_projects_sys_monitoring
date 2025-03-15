import cv2
import numpy as np
import pytesseract
import smtplib
import os
import json
import pywhatkit
import csv
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from datetime import datetime
import time
import re
from pathlib import Path

# Load environment variables
load_dotenv()

class ConfigManager:
    def __init__(self):
        self.config_file = Path('service_config.json')
        self.load_config()

    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "default_config": {
                    "email": [],
                    "whatsapp": [],
                    "whatsapp_groups": []
                },
                "services": {}
            }
            self.save_config()

    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=4)

    def get_service_config(self, service_name):
        # Use the original service name for matching
        lower_service_name = service_name.lower()

        # Try to find matching service configuration
        for config_name in self.config['services']:
            if lower_service_name == config_name.lower():
                return self.config['services'][config_name]
        
        # Return default configuration if no match found
        return self.config['default_config']

class AlertConfigUI:
    def __init__(self, parent):
        # Create a new toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Alert Configuration")
        self.window.geometry("1480x980")  # Set the window dimensions to 1480x980
        self.window.configure(bg='#F0F0F0')
        self.window.minsize(1080, 840)  # Increased minimum size by 20%
        self.window.resizable(False, False)  # Prevent the window from being resized
        
        # Create a canvas for scrolling
        self.canvas = tk.Canvas(self.window)
        self.scrollbar = tk.Scrollbar(self.window, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # Pack the canvas and scrollbar
        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Initialize feedback label
        self.feedback_label = ttk.Label(self.scrollable_frame, text="", style='Success.TLabel')

        # Apply styles
        self._setup_styles()
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Debug: Check if config is loaded
        print("Initial config loaded:", self.config_manager.config)
        
        # Create the UI
        self._create_ui()
        
        # Center the window on screen
        self.center_window()
    
    def _setup_styles(self):
        """Setup all styles for the UI"""
        style = ttk.Style(self.window)
        style.theme_use('clam')
        
        # Basic styles
        style.configure('TFrame', background='#F0F0F0')
        style.configure('TButton', padding=6)
        style.configure('TLabel', background='#F0F0F0', foreground='#000000')
        style.configure('TLabelframe', background='#F0F0F0')
        style.configure('TLabelframe.Label', background='#F0F0F0', foreground='#000000', font=('Segoe UI', 9, 'bold'))
        style.configure('TSeparator', background='#C0C0C0')
        style.configure('TNotebook', background='#F0F0F0')
        style.configure('TNotebook.Tab', padding=[10, 4], font=('Segoe UI', 9), background='#E1E1E1')
        style.configure('TEntry', fieldbackground='white', foreground='black')
        style.configure('TCombobox', fieldbackground='white', foreground='black')
        style.map('TNotebook.Tab', background=[('selected', '#F0F0F0'), ('active', '#E5E5E5')])
        
        # Custom styles
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'), background='#F0F0F0', foreground='#000000')
        style.configure('Subheader.TLabel', font=('Segoe UI', 10, 'bold'), background='#F0F0F0', foreground='#000000')
        style.configure('Hint.TLabel', font=('Segoe UI', 8), foreground='#666666', background='#F0F0F0')
        style.configure('Success.TLabel', foreground='#008800', background='#F0F0F0')
        style.configure('Error.TLabel', foreground='#CC0000', background='#F0F0F0')
        style.configure('Add.TButton', font=('Segoe UI', 9, 'bold'))
        style.configure('Delete.TButton', font=('Segoe UI', 9, 'bold'), foreground='white', background='red')  # Custom style for delete button
        
        # Make sure all child widgets inherit these styles
        self.window.option_add("*TCombobox*Listbox*Background", 'white')
        self.window.option_add("*TCombobox*Listbox*Foreground", 'black')
        self.window.option_add("*Background", '#F0F0F0')
        self.window.option_add("*Foreground", 'black')
    
    def _create_ui(self):
        """Create the main UI components"""
        # Main container with top-bottom split
        self.main_container = ttk.Frame(self.scrollable_frame)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create top frame for service list
        self._create_top_section()
        
        # Create bottom frame for service details
        self._create_bottom_section()
        
        # Create status bar at the bottom
        self._create_status_bar()
        
        # Initialize with empty details
        self.show_empty_details()
        
        # Populate service list
        self._populate_services()
        
        # Debug: Ensure the UI is fully initialized
        print("UI created and populated.")
        
        # Print the width and height of the alert configuration window
        self.window.update_idletasks()  # Ensure the window is updated before checking size
        print(f'Alert Configuration Window Size: {self.window.winfo_width()}x{self.window.winfo_height()}')
    
    def _create_top_section(self):
        """Create the top section with service list"""
        self.top_frame = ttk.Frame(self.main_container)
        self.top_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Add 'New Service' and 'Default Configuration' buttons
        self.new_service_button = ttk.Button(self.top_frame, text='+ New Service', command=self.add_new_service)
        self.new_service_button.pack(side=tk.LEFT, padx=5)

        self.default_config_button = ttk.Button(self.top_frame, text='Default Configuration', command=lambda: [self.load_default_config(), self.delete_button.pack_forget()])  # Hide the delete button when default configuration is clicked
        self.default_config_button.pack(side=tk.LEFT, padx=5)
        
        # Create Treeview for services
        self.tree = ttk.Treeview(self.main_container, columns=('Service Name', 'Email', 'WhatsApp', 'WhatsApp Groups', 'Alert Period', 'Number of Alerts'), show='headings')
        self.tree.heading('#1', text='Service Name')
        self.tree.heading('#2', text='Email')
        self.tree.heading('#3', text='WhatsApp')
        self.tree.heading('#4', text='WhatsApp Groups')
        self.tree.heading('#5', text='Alert Period')
        self.tree.heading('#6', text='Number of Alerts')
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Bind selection event
        self.tree.bind('<<TreeviewSelect>>', self._on_service_selected)
    
    def _create_bottom_section(self):
        """Create the bottom section for service details"""
        self.bottom_frame = ttk.Frame(self.main_container)
        self.bottom_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create service details frame
        self.details_frame = ttk.LabelFrame(self.bottom_frame, text="Service Configuration")
        self.details_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Debug: Ensure the bottom section is visible
        print("Bottom section created and packed.")
        
        # Add a placeholder label to ensure visibility
        placeholder_label = ttk.Label(self.details_frame, text="Service details will appear here.")
        placeholder_label.pack(pady=10)
        
        # Delete Service button
        self.delete_button = ttk.Button(self.bottom_frame, text='Delete Service', command=self.delete_service)
        self.delete_button.pack_forget()  # Hide the delete button initially
        self.delete_button.configure(style='Delete.TButton', width=25)  # Increase the width of the delete button
        
    def _create_status_bar(self):
        """Create the status bar at the bottom of the window"""
        status_frame = ttk.Frame(self.window, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Ready", padding=(10, 3))
        self.status_label.pack(side=tk.LEFT)
    
    def _on_service_selected(self, event):
        selected = self.tree.selection()
        if selected:
            service_name = self.tree.item(selected, 'text')
            self.load_service(service_name)
            self.delete_button.pack(side=tk.BOTTOM, padx=5, pady=5)  # Show the delete button
    
    def _populate_services(self):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add services to Treeview with their details
        for service_name, service_config in self.config_manager.config['services'].items():
            self.tree.insert('', 'end', text=service_name, values=(
                service_name,
                ','.join(service_config.get('email', [])),
                ','.join(service_config.get('whatsapp', [])),
                ','.join(service_config.get('whatsapp_groups', [])),
                service_config.get('period', 0),
                service_config.get('number_of_alerts', 0)
            ))
    
    def add_new_service(self):
        """Prepare UI for adding a new service"""
        self.is_new_service = True
        self.current_service = None
        self.show_service_form()
        self.status_label.configure(text="Adding new service")
    
    def load_service(self, service_name):
        """Load a service configuration into the details panel"""
        self.is_new_service = False
        self.current_service = service_name
        self.show_service_form()
        self.status_label.configure(text=f"Editing service: {service_name}")
    
    def load_default_config(self):
        """Load default configuration into the details panel"""
        self.is_new_service = False
        self.current_service = "default"
        self.show_default_form()
        self.status_label.configure(text="Editing default configuration")
    
    def show_default_form(self):
        """Show form for default configuration in the bottom section."""
        # 1) Clear whatever was in details_frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        # 2) Create a container frame inside details_frame
        form_container = ttk.Frame(self.details_frame, padding=20)
        form_container.pack(fill=tk.BOTH, expand=True)

        # 3) Header
        ttk.Label(
            form_container,
            text="Default Alert Configuration",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 10))

        # 4) Description
        ttk.Label(
            form_container,
            text="These settings will be used when no specific service configuration matches.",
            wraplength=700
        ).pack(anchor=tk.W, pady=(0, 15))

        # ====================== 
        #  Email Notifications
        # ====================== 
        email_frame = ttk.LabelFrame(form_container, text="Email Notifications")
        email_frame.pack(fill=tk.X, pady=(0, 15))

        email_inner = ttk.Frame(email_frame, padding=10)
        email_inner.pack(fill=tk.X)

        ttk.Label(email_inner, text="Email Addresses:").pack(anchor=tk.W, pady=(0, 5))

        self.default_email = ttk.Entry(email_inner, width=60)
        self.default_email.pack(fill=tk.X, pady=(0, 5))

        # Insert existing default emails from config
        default_emails = self.config_manager.config['default_config'].get('email', [])
        self.default_email.insert(0, ','.join(default_emails))

        ttk.Label(
            email_inner,
            text="Separate multiple addresses with commas (e.g., user@example.com, another@example.com)",
            style='Hint.TLabel'
        ).pack(anchor=tk.W)

        # ========================= 
        #  WhatsApp Notifications
        # ========================= 
        whatsapp_frame = ttk.LabelFrame(form_container, text="WhatsApp Notifications")
        whatsapp_frame.pack(fill=tk.X, pady=(0, 15))

        whatsapp_inner = ttk.Frame(whatsapp_frame, padding=10)
        whatsapp_inner.pack(fill=tk.X)

        # --- WhatsApp Numbers ---
        ttk.Label(whatsapp_inner, text="WhatsApp Numbers:").pack(anchor=tk.W, pady=(0, 5))

        self.default_whatsapp = ttk.Entry(whatsapp_inner, width=60)
        self.default_whatsapp.pack(fill=tk.X, pady=(0, 5))

        default_whatsapp_nums = self.config_manager.config['default_config'].get('whatsapp', [])
        self.default_whatsapp.insert(0, ','.join(default_whatsapp_nums))

        ttk.Label(
            whatsapp_inner,
            text="Separate multiple numbers with commas (include country code, e.g., +1234567890)",
            style='Hint.TLabel'
        ).pack(anchor=tk.W)

        # --- WhatsApp Groups (optional) ---
        ttk.Label(whatsapp_inner, text="WhatsApp Groups:").pack(anchor=tk.W, pady=(10, 5))

        self.default_whatsapp_groups = ttk.Entry(whatsapp_inner, width=60)
        self.default_whatsapp_groups.pack(fill=tk.X, pady=(0, 5))

        default_whatsapp_grps = self.config_manager.config['default_config'].get('whatsapp_groups', [])
        self.default_whatsapp_groups.insert(0, ','.join(default_whatsapp_grps))

        ttk.Label(
            whatsapp_inner,
            text="Separate multiple group IDs or links with commas",
            style='Hint.TLabel'
        ).pack(anchor=tk.W)

        # ========================= 
        #  Buttons (Save/Cancel)
        # ========================= 
        button_frame = ttk.Frame(form_container)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        self.feedback_label = ttk.Label(button_frame, text="", style='Success.TLabel')
        self.feedback_label.pack(side=tk.LEFT, padx=5)

        save_btn = ttk.Button(
            button_frame,
            text="Save Changes",
            command=self.save_default_config,
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: [self.show_empty_details(), self.delete_button.pack_forget()],  # Hide the delete button when cancel is clicked
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def save_default_config(self):
        # Gather fields
        emails = [e.strip() for e in self.default_email.get().split(',') if e.strip()]
        whatsapp_nums = [w.strip() for w in self.default_whatsapp.get().split(',') if w.strip()]
        whatsapp_grps = [g.strip() for g in self.default_whatsapp_groups.get().split(',') if g.strip()]

        # Update config
        self.config_manager.config['default_config']['email'] = emails
        self.config_manager.config['default_config']['whatsapp'] = whatsapp_nums
        self.config_manager.config['default_config']['whatsapp_groups'] = whatsapp_grps

        # Save to file
        self.config_manager.save_config()

        # Feedback
        if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists():
            self.feedback_label.configure(text="Default configuration saved successfully!", style='Success.TLabel')
            self.status_label.configure(text="Default configuration saved")
        
        # Clear feedback after 3 seconds
        self.details_frame.after(3000, lambda: self.feedback_label.configure(text="") if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists() else None)
    
    def save_service(self):
        # Get the new service name
        new_name = self.service_name_var.get().strip()

        # If this is a new service, ensure old_name is not None
        if self.is_new_service:
            old_name = None
        else:
            old_name = self.current_service

        # If old_name exists, copy its config to the new name
        if old_name:
            self.config_manager.config['services'][new_name] = self.config_manager.config['services'][old_name]
            if old_name != new_name:
                del self.config_manager.config['services'][old_name]
        else:
            # Create a new service entry
            self.config_manager.config['services'][new_name] = {
                'email': [],
                'whatsapp': [],
                'whatsapp_groups': [],
                'period': 0,
                'number_of_alerts': 0
            }

        # Now update the email/WhatsApp fields
        email_list = [e.strip() for e in self.service_email.get().split(',') if e.strip()]
        whatsapp_list = [w.strip() for w in self.service_whatsapp.get().split(',') if w.strip()]
        whatsapp_groups_list = [g.strip() for g in self.service_whatsapp_groups.get().split(',') if g.strip()]
        period = int(self.period_entry.get())
        number_of_alerts = int(self.number_of_alerts_entry.get())

        self.config_manager.config['services'][new_name].update({
            'email': email_list,
            'whatsapp': whatsapp_list,
            'whatsapp_groups': whatsapp_groups_list,
            'period': period,
            'number_of_alerts': number_of_alerts
        })

        # Save the updated config
        self.config_manager.save_config()

        # Show success feedback
        if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists():
            self.feedback_label.configure(
                text=f"Service '{new_name}' saved successfully!",
                style='Success.TLabel'
            )
            self.status_label.configure(text=f"Service '{new_name}' saved")

            # Clear the feedback after a few seconds
            self.details_frame.after(3000, lambda: self.feedback_label.configure(text="") if hasattr(self, 'feedback_label') and self.feedback_label.winfo_exists() else None)

        # Re-populate the service list to reflect the new name
        self._populate_services()

    def delete_service(self):
        """Delete the current service"""
        if not self.current_service or self.current_service == "default":
            return
        
        # Confirm deletion
        if not tk.messagebox.askyesno("Confirm Delete", 
                                    f"Are you sure you want to delete '{self.current_service}'?",
                                    parent=self.window):
            return
        
        # Delete service
        service_name = self.current_service
        del self.config_manager.config['services'][service_name]
        
        # Save configuration
        self.config_manager.save_config()
        
        # Update UI
        self.current_service = None
        self.is_new_service = False
        self._populate_services()
        self.show_empty_details()
        
        # Show feedback
        self.status_label.configure(text=f"Service '{service_name}' deleted")
    
    def save_configuration(self):
        """Save all configuration changes and close window"""
        self.config_manager.save_config()
        self.status_label.configure(text="Configuration saved successfully")
        self.window.destroy()

    def show_service_form(self):
        """Show form for editing an existing service (non-default)."""
        # 1) Clear the details_frame
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        form_container = ttk.Frame(self.details_frame, padding=20)
        form_container.pack(fill=tk.BOTH, expand=True)

        # 2) Header
        ttk.Label(
            form_container,
            text=f"Edit Service: {self.current_service}",
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))

        # 3) Retrieve the existing config
        service_config = self.config_manager.config['services'].get(self.current_service, {})

        # 4) Create text fields for email, WhatsApp, etc.
        # Service Name field
        ttk.Label(form_container, text="Service Name:").pack(anchor=tk.W, pady=(0, 5))
        self.service_name_var = tk.StringVar(value=self.current_service)
        self.service_name_entry = ttk.Entry(form_container, width=60, textvariable=self.service_name_var)
        self.service_name_entry.pack(fill=tk.X, pady=(0, 5))

        # Email field
        ttk.Label(form_container, text="Email Addresses:").pack(anchor=tk.W, pady=(0, 5))
        self.service_email = ttk.Entry(form_container, width=60)
        self.service_email.pack(fill=tk.X, pady=(0, 5))
        self.service_email.insert(0, ','.join(service_config.get('email', [])))

        # WhatsApp Numbers field
        ttk.Label(form_container, text="WhatsApp Numbers:").pack(anchor=tk.W, pady=(0, 5))
        self.service_whatsapp = ttk.Entry(form_container, width=60)
        self.service_whatsapp.pack(fill=tk.X, pady=(0, 5))
        self.service_whatsapp.insert(0, ','.join(service_config.get('whatsapp', [])))

        # WhatsApp Groups field
        ttk.Label(form_container, text="WhatsApp Groups:").pack(anchor=tk.W, pady=(0, 5))
        self.service_whatsapp_groups = ttk.Entry(form_container, width=60)
        self.service_whatsapp_groups.pack(fill=tk.X, pady=(0, 5))
        self.service_whatsapp_groups.insert(0, ','.join(service_config.get('whatsapp_groups', [])))

        # Add fields for period and number of alerts
        period_frame = ttk.LabelFrame(form_container, text="Alert Settings")
        period_frame.pack(fill=tk.X, pady=(0, 15))

        # Period field
        ttk.Label(period_frame, text="Alert Period (minutes):").pack(anchor=tk.W, pady=(0, 5))
        self.period_entry = ttk.Entry(period_frame, width=60)
        self.period_entry.pack(fill=tk.X, pady=(0, 5))
        self.period_entry.insert(0, str(service_config.get('period', 0)))  # Default value

        # Number of Alerts field
        ttk.Label(period_frame, text="Number of Alerts:").pack(anchor=tk.W, pady=(0, 5))
        self.number_of_alerts_entry = ttk.Entry(period_frame, width=60)
        self.number_of_alerts_entry.pack(fill=tk.X, pady=(0, 5))
        self.number_of_alerts_entry.insert(0, str(service_config.get('number_of_alerts', 0)))  # Default value

        # 5) Create a Save button that calls save_service()
        button_frame = ttk.Frame(form_container)
        button_frame.pack(fill=tk.X, pady=(20, 0))

        save_btn = ttk.Button(
            button_frame,
            text="Save",
            command=self.save_service,
            width=15
        )
        save_btn.pack(side=tk.RIGHT, padx=5)

        cancel_btn = ttk.Button(
            button_frame,
            text="Cancel",
            command=lambda: [self.show_empty_details(), self.delete_button.pack_forget()],  # Hide the delete button when cancel is clicked
            width=15
        )
        cancel_btn.pack(side=tk.RIGHT, padx=5)

    def show_empty_details(self):
        """Show empty details panel with message"""
        # Clear existing widgets
        for widget in self.details_frame.winfo_children():
            widget.destroy()
        
        # Show message
        message_frame = ttk.Frame(self.details_frame)
        message_frame.pack(expand=True, fill=tk.BOTH)
        
        ttk.Label(message_frame, text="Select a service from the list or create a new one",
                style='Subheader.TLabel').pack(expand=True)
    
    def center_window(self):
        """Center the window on the screen"""
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')

class CreateToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create tooltip content
        frame = ttk.Frame(self.tooltip, borderwidth=1, relief="solid")
        frame.pack(fill="both", expand=True)
        
        label = ttk.Label(frame, text=self.text, wraplength=250, 
                        background="#FFFFDD", foreground="black", 
                        padding=(5, 3))
        label.pack()
    
    def on_leave(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class DashboardMonitor:
    def __init__(self):
        self.camera = None
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        # Initialize configuration manager
        self.config_manager = ConfigManager()
        
        # Define color thresholds for red and green in HSV
        self.red_lower = np.array([0, 120, 70])
        self.red_upper = np.array([10, 255, 255])
        self.green_lower = np.array([35, 120, 70])
        self.green_upper = np.array([85, 255, 255])

        # Create logs directory if it doesn't exist
        self.logs_dir = Path('service_logs')
        self.logs_dir.mkdir(exist_ok=True)

        # Initialize UI
        self.root = None
        self.camera_var = None

    def show_ui(self):
        """Display the desktop UI for camera selection"""
        self.root = tk.Tk()
        self.root.title("Service Monitoring System")
        self.root.geometry("800x500")
        
        # Set light theme for Windows-like appearance
        self.root.configure(bg='#F0F0F0')
        
        # Style configuration for Windows-like appearance
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
        
        # Create menu bar
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
        
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create notebook (tabbed interface)
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
        start_btn = ttk.Button(button_frame, text="Start Monitoring", width=20,
                              command=self.start_monitoring)
        start_btn.pack(side=tk.RIGHT, padx=5)
        
        config_btn = ttk.Button(button_frame, text="Alert Configuration", width=20,
                               command=lambda: AlertConfigUI(self.root))
        config_btn.pack(side=tk.RIGHT, padx=5)
        
        # Initial camera detection
        self.update_camera_list(camera_dropdown, start_btn)
        
        # Center window
        self.center_window()
        
        self.root.mainloop()
    
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
        ttk.Label(frame, text=" 2025 All Rights Reserved").pack(pady=(10, 0))
        
        ttk.Button(frame, text="OK", command=about_window.destroy, width=10).pack(pady=20)

    def update_camera_list(self, camera_dropdown, start_btn):
        """Update the camera dropdown list and monitoring button state"""
        available_cameras = self.list_cameras()
        
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

    def start_monitoring(self):
        """Start monitoring with selected camera"""
        if not self.camera_var:
            return
            
        selected_camera = self.camera_var.get()
        camera_id = int(re.search(r'ID: (\d+)', selected_camera).group(1))
        
        self.camera = cv2.VideoCapture(camera_id, cv2.CAP_V4L2)
        if not self.camera.isOpened():
            messagebox.showerror("Error", f"Failed to initialize camera {camera_id}")
            return
            
        self.root.destroy()
        self.monitor()

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
        message = " ALERT: Service Down - {service_name}\n"
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

        recipients = config.get("email", [])
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

    def _get_service_config(self, service_name):
        """Get configuration for a specific service"""
        return self.config_manager.get_service_config(service_name)

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

if __name__ == "__main__":
    monitor = DashboardMonitor()
    monitor.show_ui()
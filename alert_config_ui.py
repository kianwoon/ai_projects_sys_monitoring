"""
Alert Configuration UI Module
"""
import tkinter as tk
from tkinter import ttk, messagebox

from config_manager import ConfigManager

class AlertConfigUI:
    """UI for configuring alert settings"""
    def __init__(self, parent):
        # Initialize variables first
        self.is_new_service = False
        self.current_service = None
        self.service_name_var = tk.StringVar()
        self.service_email = tk.StringVar()
        self.service_whatsapp = tk.StringVar()
        self.service_whatsapp_groups = tk.StringVar()
        
        # Create a new toplevel window
        self.window = tk.Toplevel(parent)
        self.window.title("Alert Configuration")
        self.window.geometry('1500x1300')  # Set the main window size to 1500x1300
        self.window.minsize(1500, 1300)  # Set minimum size to accommodate new dimensions
        self.window.configure(bg='#F0F0F0')
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
        
        # Create status bar at the bottom of the window
        status_frame = ttk.Frame(self.window, relief=tk.SUNKEN, borderwidth=1)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_label = ttk.Label(status_frame, text="Ready", padding=(10, 3))
        self.status_label.pack(side=tk.LEFT)
        
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

        self.default_config_button = ttk.Button(
            self.top_frame, 
            text='Default Configuration', 
            command=lambda: [self.load_default_config(), self.delete_button.pack_forget()]
        )
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
    
    def _on_service_selected(self, event):
        """Handle selection in the service treeview"""
        selected = self.tree.selection()
        if selected:
            # Get the actual service name from the first column value instead of the 'text' property
            service_name = self.tree.item(selected, 'values')[0]
            print(f"Selected service: {service_name}")  # Debug print
            
            # Check if service exists in config before loading
            if service_name in self.config_manager.config['services']:
                self.load_service(service_name)
                self.delete_button.pack(side=tk.BOTTOM, padx=5, pady=5)  # Show the delete button
            else:
                print(f"Warning: Selected service '{service_name}' not found in configuration")

    def _populate_services(self):
        """Populate the service list treeview with services from the configuration"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add services to Treeview with their details
        for service_name, service_config in self.config_manager.config['services'].items():
            # Check if the item already exists
            if not self.tree.exists(service_name):
                # Insert the item with service_name as both the identifier and the first column value
                self.tree.insert('', 'end', iid=service_name, text=service_name, values=(
                    service_name,  # First column is service name
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
        if not new_name:
            # Display an error message if service name is empty
            messagebox.showerror("Error", "Service name cannot be empty", parent=self.window)
            return

        # If this is a new service, ensure old_name is not None
        if self.is_new_service:
            old_name = None
        else:
            old_name = self.current_service

        # If old_name exists, copy its config to the new name
        if old_name and old_name in self.config_manager.config['services']:
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
        
        # Get period value with error handling
        try:
            period_str = self.period_entry.get().strip()
            period = int(period_str) if period_str else 0
        except ValueError:
            period = 0
            messagebox.showwarning("Warning", "Invalid period value. Using default value 0.", parent=self.window)

        # Get number of alerts with error handling
        try:
            number_of_alerts_str = self.number_of_alerts_entry.get().strip()
            number_of_alerts = int(number_of_alerts_str) if number_of_alerts_str else 0
        except ValueError:
            number_of_alerts = 0
            messagebox.showwarning("Warning", "Invalid number of alerts. Using default value 0.", parent=self.window)

        # Update the configuration
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
        if not messagebox.askyesno("Confirm Delete", 
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
        header_text = "Add New Service" if self.is_new_service else f"Edit Service: {self.current_service}"
        ttk.Label(
            form_container,
            text=header_text,
            style='Header.TLabel'
        ).pack(anchor=tk.W, pady=(0, 20))

        # 3) Retrieve the existing config
        service_config = self.config_manager.config['services'].get(self.current_service, {})

        # 4) Create text fields for email, WhatsApp, etc.
        # Service Name field
        ttk.Label(form_container, text="Service Name:").pack(anchor=tk.W, pady=(0, 5))
        self.service_name_var.set(self.current_service or "")
        self.service_name_entry = ttk.Entry(form_container, width=60, textvariable=self.service_name_var)
        self.service_name_entry.pack(fill=tk.X, pady=(0, 5))

        # Email field
        ttk.Label(form_container, text="Email Addresses:").pack(anchor=tk.W, pady=(0, 5))
        self.service_email.set(','.join(service_config.get('email', [])))
        self.service_email_entry = ttk.Entry(form_container, width=60, textvariable=self.service_email)
        self.service_email_entry.pack(fill=tk.X, pady=(0, 5))

        # WhatsApp Numbers field
        ttk.Label(form_container, text="WhatsApp Numbers:").pack(anchor=tk.W, pady=(0, 5))
        self.service_whatsapp.set(','.join(service_config.get('whatsapp', [])))
        self.service_whatsapp_entry = ttk.Entry(form_container, width=60, textvariable=self.service_whatsapp)
        self.service_whatsapp_entry.pack(fill=tk.X, pady=(0, 5))

        # WhatsApp Groups field
        ttk.Label(form_container, text="WhatsApp Groups:").pack(anchor=tk.W, pady=(0, 5))
        self.service_whatsapp_groups.set(','.join(service_config.get('whatsapp_groups', [])))
        self.service_whatsapp_groups_entry = ttk.Entry(form_container, width=60, textvariable=self.service_whatsapp_groups)
        self.service_whatsapp_groups_entry.pack(fill=tk.X, pady=(0, 5))

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

        self.feedback_label = ttk.Label(button_frame, text="", style='Success.TLabel')
        self.feedback_label.pack(side=tk.LEFT, padx=5)

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
        self.window.update_idletasks()  # Ensure sizes are updated
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        print('Main screen dimensions:', self.window.winfo_width(), 'x', self.window.winfo_height())  # Debug statement to print dimensions
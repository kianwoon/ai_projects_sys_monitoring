"""
UI Utilities for Service Monitor
"""
import tkinter as tk
from tkinter import ttk

class CreateToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.on_enter)
        self.widget.bind("<Leave>", self.on_leave)
    
    def on_enter(self, event=None):
        """Show tooltip when mouse enters widget"""
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
        """Hide tooltip when mouse leaves widget"""
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None
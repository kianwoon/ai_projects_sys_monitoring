#!/usr/bin/env python3
"""
Service Monitoring System - Main Entry Point
"""
from dotenv import load_dotenv
from dashboard_monitor import DashboardMonitor

# Load environment variables from .env file
load_dotenv()

def main():
    """Main entry point for the application"""
    monitor = DashboardMonitor()
    monitor.show_ui()

if __name__ == "__main__":
    main()
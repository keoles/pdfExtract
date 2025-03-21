#!/usr/bin/env python3
"""
Development mode script for Art Data Extract
Monitors the src directory for changes and automatically restarts the GUI
"""

import os
import sys
import time
import subprocess
import signal
import hashlib
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# Add the parent directory to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

# Define which files to watch
WATCH_PATHS = [
    os.path.join(project_root, "src/gui"),
    os.path.join(project_root, "src/core"),
    os.path.join(project_root, "src/utils"),
    os.path.join(project_root, "resources")
]

# The command to run the GUI app
GUI_APP_CMD = [sys.executable, os.path.join(project_root, "src/gui/messages_sync_app.py")]
GUI_PDF_EXTRACTOR_CMD = [sys.executable, os.path.join(project_root, "src/gui/imessage_pdf_extract_gui.py")]

# Global process reference
current_process = None

class SourceCodeChangeHandler(FileSystemEventHandler):
    def __init__(self, restart_callback):
        self.restart_callback = restart_callback
        self.file_hashes = {}
        self.initialize_file_hashes()
        
    def initialize_file_hashes(self):
        """Initialize the hash values of all Python files in watched directories"""
        for watch_path in WATCH_PATHS:
            if os.path.isdir(watch_path):
                for root, _, files in os.walk(watch_path):
                    for file in files:
                        if file.endswith(('.py', '.png', '.json')):
                            filepath = os.path.join(root, file)
                            self.file_hashes[filepath] = self.get_file_hash(filepath)
    
    def get_file_hash(self, filepath):
        """Compute a hash of the file contents"""
        try:
            with open(filepath, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return None
    
    def on_modified(self, event):
        """Called when a file or directory is modified"""
        if not event.is_directory and event.src_path.endswith(('.py', '.png', '.json')):
            # Calculate new hash
            new_hash = self.get_file_hash(event.src_path)
            old_hash = self.file_hashes.get(event.src_path)
            
            # If the hash changed, update it and restart
            if new_hash != old_hash:
                self.file_hashes[event.src_path] = new_hash
                print(f"\n🔄 File changed: {os.path.basename(event.src_path)}")
                self.restart_callback()
    
    def on_created(self, event):
        """Called when a file or directory is created"""
        if not event.is_directory and event.src_path.endswith(('.py', '.png', '.json')):
            self.file_hashes[event.src_path] = self.get_file_hash(event.src_path)
            print(f"\n➕ New file: {os.path.basename(event.src_path)}")
            self.restart_callback()

def start_app(use_pdf_extractor=False):
    """Start the GUI application"""
    global current_process
    
    # Kill existing process if it exists
    if current_process:
        try:
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
        except:
            pass
    
    # Start a new process
    cmd = GUI_PDF_EXTRACTOR_CMD if use_pdf_extractor else GUI_APP_CMD
    print(f"\n🚀 Starting {'PDF Extractor' if use_pdf_extractor else 'Messages Sync App'}...")
    current_process = subprocess.Popen(
        cmd, 
        stdout=subprocess.PIPE, 
        stderr=subprocess.STDOUT,
        preexec_fn=os.setsid  # Create a new process group
    )
    
    # Print the process ID
    print(f"Process started with PID: {current_process.pid}")

def restart_app():
    """Restart the application with the same parameters"""
    global current_process
    if current_process:
        # Check which app is running
        using_pdf_extractor = current_process.args == GUI_PDF_EXTRACTOR_CMD
        start_app(use_pdf_extractor=using_pdf_extractor)

def monitor_process_output():
    """Monitor and print the process output"""
    if current_process:
        while current_process.poll() is None:
            output = current_process.stdout.readline()
            if output:
                print(output.decode('utf-8').strip())
            time.sleep(0.1)

def main():
    """Main function to set up file watching and start the application"""
    # Default to the main app unless specified otherwise
    app_choice = input("Which app to run? (1) Messages Sync App or (2) PDF Extractor [1/2]: ").strip()
    use_pdf_extractor = app_choice == "2"
    
    # Set up the event handler and observer
    event_handler = SourceCodeChangeHandler(restart_app)
    observer = Observer()
    
    # Schedule the directories to watch
    for watch_path in WATCH_PATHS:
        if os.path.isdir(watch_path):
            observer.schedule(event_handler, watch_path, recursive=True)
    
    # Start the observer
    observer.start()
    
    try:
        print("\n🔍 Watching for changes in source files...")
        print("Press Ctrl+C to stop the development mode.")
        
        # Start the application
        start_app(use_pdf_extractor)
        
        # Monitor output in a loop
        while True:
            # Check if process is still running, restart if it crashed
            if current_process and current_process.poll() is not None:
                print("⚠️ Application crashed, restarting...")
                start_app(use_pdf_extractor)
            
            monitor_process_output()
            time.sleep(0.5)
    
    except KeyboardInterrupt:
        print("\n🛑 Development mode stopped")
    finally:
        # Stop the observer
        observer.stop()
        observer.join()
        
        # Kill the application if it's still running
        if current_process:
            try:
                os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
                print("Application terminated")
            except:
                pass

if __name__ == "__main__":
    main() 
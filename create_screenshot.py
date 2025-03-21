#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk
import os
from PIL import ImageGrab, Image
import time
import sys

def capture_window(window, filename):
    """Capture a screenshot of the window and save it to a file"""
    # Make sure window is fully visible and updated
    window.update_idletasks()
    window.update()
    
    # Wait for window to be fully drawn
    time.sleep(0.5)
    
    # Get window geometry
    x = window.winfo_rootx()
    y = window.winfo_rooty()
    width = window.winfo_width()
    height = window.winfo_height()
    
    # Capture the window
    img = ImageGrab.grab(bbox=(x, y, x+width, y+height))
    
    # Save the screenshot
    img.save(filename)
    print(f"Screenshot saved to {filename}")

class DemoMessagesSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("iMessage Sync Tool")
        self.root.geometry("400x560")
        self.root.resizable(False, False)
        
        # Configure styles with a more modern look
        self.style = ttk.Style()
        self.style.configure("TFrame", background="#f5f7fa")
        self.style.configure("TButton", font=("SF Pro Display", 12))
        self.style.configure("TLabel", font=("SF Pro Display", 12), background="#f5f7fa")
        self.style.configure("Header.TLabel", font=("SF Pro Display", 22, "bold"), foreground="#333333", background="#f5f7fa")
        self.style.configure("Instructions.TLabel", font=("SF Pro Display", 11), background="#f5f7fa", wraplength=360, foreground="#555555")
        
        # Configure custom button styles - more modern and macOS-like
        self.style.configure("Blue.TButton", 
                            padding=(10, 8),
                            font=("SF Pro Display", 12, "bold"))
        
        self.style.map("Blue.TButton",
                      background=[("active", "#2980b9"), ("!disabled", "#3498db")],
                      foreground=[("!disabled", "#ffffff")])
        
        self.style.configure("Success.TButton", 
                            padding=(10, 8),
                            font=("SF Pro Display", 12, "bold"))
        
        self.style.map("Success.TButton",
                      background=[("active", "#27ae60"), ("!disabled", "#2ecc71")],
                      foreground=[("!disabled", "#ffffff")])
        
        self.style.configure("Next.TButton", 
                            padding=(10, 8),
                            font=("SF Pro Display", 12, "bold"))
        
        self.style.map("Next.TButton",
                      background=[("active", "#d35400"), ("!disabled", "#f39c12")],
                      foreground=[("!disabled", "#ffffff")])
        
        # Configure separator style
        self.style.configure("TSeparator", background="#dddddd")
        
        # Main frame
        self.main_frame = ttk.Frame(root, padding="20", style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_label = ttk.Label(
            self.main_frame, 
            text="iMessage Sync", 
            style="Header.TLabel"
        )
        self.header_label.pack(pady=(5, 15), anchor="w")
        
        # Subheader
        self.subheader_label = ttk.Label(
            self.main_frame,
            text="Sync your messages and extract attachments",
            font=("SF Pro Display", 12),
            foreground="#777777",
            background="#f5f7fa"
        )
        self.subheader_label.pack(pady=(0, 20), anchor="w")
        
        # Main card frame
        self.card_frame = ttk.Frame(self.main_frame, padding="15", style="Card.TFrame")
        self.card_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Apply a light background and border to card
        self.style.configure("Card.TFrame", background="white", relief="flat")
        
        # Create a canvas for rounded corners effect
        self.card_canvas = tk.Canvas(self.card_frame, bg="white", highlightthickness=0)
        self.card_canvas.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Instructions label
        instructions_text = (
            "To sync your iMessages, please follow these steps:"
            "\n\n1. Click 'Step 1: Open Message Settings' button below"
            "\n2. The Messages app will open with the preferences window"
            "\n3. Select the 'iMessage' tab"
            "\n4. Click the 'Sync Now' button"
            "\n5. Wait for syncing to complete"
            "\n6. Click the 'Step 2: Confirm Sync Complete' button below"
            "\n7. After confirmation, the 'Step 3' button will be enabled"
        )
        
        self.instructions_label = ttk.Label(
            self.card_frame,
            text=instructions_text,
            style="Instructions.TLabel",
            justify="left",
            background="white"
        )
        self.instructions_label.pack(pady=10, fill="x")
        
        # Spacer
        ttk.Separator(self.card_frame, orient="horizontal").pack(fill="x", pady=15)
        
        # Step indicators (circles)
        self.steps_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        self.steps_frame.pack(pady=5, fill="x")
        
        # Three step indicators side by side
        step_texts = ["Open Settings", "Sync Messages", "Continue"]
        
        for i in range(3):
            frame = ttk.Frame(self.steps_frame, style="Card.TFrame")
            frame.pack(side=tk.LEFT, expand=True)
            
            # Create colored circle
            color = "#dddddd"  # Default gray
            if i == 0:
                color = "#3498db"  # Blue for current step
            
            circle_size = 24
            circle_canvas = tk.Canvas(frame, width=circle_size, height=circle_size,
                                    bg="white", highlightthickness=0)
            circle_canvas.pack(pady=5)
            circle_canvas.create_oval(2, 2, circle_size-2, circle_size-2, fill=color, outline="")
            
            # Step number in circle
            circle_canvas.create_text(circle_size//2, circle_size//2, text=str(i+1),
                                    fill="white", font=("SF Pro Display", 10, "bold"))
            
            # Step text
            step_label = ttk.Label(frame, text=step_texts[i], 
                                 font=("SF Pro Display", 9), foreground="#777777",
                                 background="white")
            step_label.pack(pady=2)
        
        # Button container frame
        self.button_frame = ttk.Frame(self.card_frame, style="Card.TFrame")
        self.button_frame.pack(pady=15, fill="x")
        
        # Open Message Preferences button
        self.open_preferences_button = ttk.Button(
            self.button_frame,
            text="Step 1: Open Message Settings",
            command=lambda: None,
            style="Blue.TButton",
            width=30
        )
        self.open_preferences_button.pack(pady=8)
        
        # Confirmation button
        self.confirm_button = ttk.Button(
            self.button_frame,
            text="Step 2: Confirm Sync Complete",
            command=lambda: None,
            style="TButton",
            width=30
        )
        self.confirm_button.pack(pady=8)
        
        # Next button to navigate to PDF retrieval page
        self.next_button = ttk.Button(
            self.button_frame,
            text="Step 3: Extract PDFs →",
            command=lambda: None,
            style="Next.TButton",
            width=30,
            state="disabled"  # Initially disabled
        )
        self.next_button.pack(pady=8)
        
        # Last sync time
        self.last_sync_label = ttk.Label(
            self.card_frame,
            text="No previous sync recorded",
            font=("SF Pro Display", 10),
            foreground="#888888",
            background="white"
        )
        self.last_sync_label.pack(pady=10)
        
        # Footer
        self.footer_label = ttk.Label(
            self.main_frame,
            text="iMessage Sync Tool",
            font=("SF Pro Display", 9),
            foreground="#999999",
            background="#f5f7fa"
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(15, 0))
        
        # Version
        self.version_label = ttk.Label(
            self.main_frame,
            text="v2.1",
            font=("SF Pro Display", 8),
            foreground="#999999",
            background="#f5f7fa"
        )
        self.version_label.pack(side=tk.BOTTOM, pady=(0, 5))

def create_screenshot():
    root = tk.Tk()
    app = DemoMessagesSyncApp(root)
    
    # Make sure the window is drawn
    root.update_idletasks()
    root.update()
    
    # Capture screenshot
    filename = "screenshot.png"
    capture_window(root, filename)
    
    # Close the window
    root.destroy()

if __name__ == "__main__":
    create_screenshot()
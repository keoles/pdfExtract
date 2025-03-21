#!/usr/bin/env python3
import tkinter as tk
from tkinter import ttk, messagebox
import threading
import os
import json
import datetime
import subprocess

class MessagesSyncApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Art Data Extract")
        self.root.geometry("500x640")
        self.root.resizable(False, False)
        
        # Set app icon if available
        icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icon.png")
        if os.path.exists(icon_path):
            icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, icon)
        
        # Configure dark theme colors
        self.colors = {
            "bg_dark": "#2e3440",         # Dark background
            "bg_card": "#3b4252",         # Card background
            "text_light": "#e5e9f0",      # Light text
            "text_dim": "#d8dee9",        # Dimmed text
            "accent": "#88c0d0",          # Accent color (blue)
            "accent_hover": "#8fbcbb",    # Accent hover
            "secondary": "#81a1c1",       # Secondary accent
            "disabled": "#4c566a",        # Disabled state
            "success": "#a3be8c",         # Success/confirm color
            "extract": "#b48ead"          # Extract color
        }
        
        # Configure styles
        self.configure_styles()
        
        # Track sync status
        self.sync_completed = False
        
        # Main frame
        self.main_frame = tk.Frame(root, bg=self.colors["bg_dark"], padx=25, pady=25)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header
        self.header_label = tk.Label(
            self.main_frame, 
            text="Art Data Extract", 
            font=("SF Pro Display", 32, "bold"),
            fg=self.colors["text_light"],
            bg=self.colors["bg_dark"]
        )
        self.header_label.pack(pady=(5, 5), anchor="w")
        
        # Subheader
        self.subheader_label = tk.Label(
            self.main_frame,
            text="Sync your messages and extract attachments",
            font=("SF Pro Display", 14),
            fg=self.colors["text_dim"],
            bg=self.colors["bg_dark"]
        )
        self.subheader_label.pack(pady=(0, 20), anchor="w")
        
        # Main card frame
        self.card_frame = tk.Frame(self.main_frame, bg=self.colors["bg_card"], padx=25, pady=25)
        self.card_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        # Instructions label
        instructions_text = (
            "To sync your iMessages, please follow these steps:"
        )
        
        self.instructions_label = tk.Label(
            self.card_frame,
            text=instructions_text,
            font=("SF Pro Display", 14, "bold"),
            fg=self.colors["text_light"],
            bg=self.colors["bg_card"],
            justify="left"
        )
        self.instructions_label.pack(pady=(0, 15), anchor="w")
        
        # Steps instructions in a scrollable frame
        steps_text = (
            "1. Click '1: OPEN SETTINGS' button below\n"
            "2. The Messages app will open with the preferences window\n"
            "3. Select the 'iMessage' tab\n"
            "4. Click the 'Sync Now' button\n"
            "5. Wait for syncing to complete\n"
            "6. Click the '2: CONFIRM SYNC' button below\n"
            "7. After confirmation, the '3: EXTRACT MY PDFs' button will be enabled"
        )
        
        steps_frame = tk.Frame(self.card_frame, bg=self.colors["bg_card"])
        steps_frame.pack(fill="x", expand=False, pady=(0, 15))
        
        self.steps_label = tk.Label(
            steps_frame,
            text=steps_text,
            font=("SF Pro Display", 12),
            fg=self.colors["text_dim"],
            bg=self.colors["bg_card"],
            justify="left",
            anchor="w"
        )
        self.steps_label.pack(fill="x", expand=True, padx=10)
        
        # Step indicators (circles with progress)
        self.steps_indicator_frame = tk.Frame(self.card_frame, bg=self.colors["bg_card"])
        self.steps_indicator_frame.pack(pady=15, fill="x")
        
        # Create the progress steps
        self.progress_frames = []
        
        # STEP 1 - Open Messages
        step1_frame = self.create_step_frame(1, "Open Messages", True)
        self.progress_frames.append(step1_frame)
        
        # STEP 2 - Sync Messages
        step2_frame = self.create_step_frame(2, "Sync Messages", False)
        self.progress_frames.append(step2_frame)
        
        # STEP 3 - Extract PDFs
        step3_frame = self.create_step_frame(3, "Extract PDFs", False)
        self.progress_frames.append(step3_frame)
        
        # Button container frame
        self.button_frame = tk.Frame(self.card_frame, bg=self.colors["bg_card"])
        self.button_frame.pack(pady=20, fill="x")
        
        # Create a frame for even button spacing
        self.button_grid_frame = tk.Frame(self.button_frame, bg=self.colors["bg_card"])
        self.button_grid_frame.pack(fill="x", expand=True)
        
        # Create left column
        self.left_column = tk.Frame(self.button_grid_frame, bg=self.colors["bg_card"])
        self.left_column.grid(row=0, column=0, padx=(0, 10))
        
        # Create right column
        self.right_column = tk.Frame(self.button_grid_frame, bg=self.colors["bg_card"])
        self.right_column.grid(row=0, column=1, padx=(10, 0))
        
        # Configure grid to make columns equal width
        self.button_grid_frame.grid_columnconfigure(0, weight=1)
        self.button_grid_frame.grid_columnconfigure(1, weight=1)
        
        # Open Message Preferences button - smaller size with better contrast
        button_bg_color = "#434c5e"       # Darker button background for contrast
        button_hover_color = "#4c566a"    # Slightly lighter on hover
        button_text_color = "#eceff4"     # Bright white text for contrast
        
        self.open_messages_button = self.create_button(
            self.left_column,
            "1: OPEN SETTINGS",
            self.open_message_preferences,
            button_bg_color,
            button_hover_color,
            width=16,   # Make button width smaller
            font_size=12,
            text_color=button_text_color
        )
        
        # Confirmation button - match size of Open Settings button with same styling
        self.confirm_button = self.create_button(
            self.right_column,
            "2: CONFIRM SYNC",
            self.confirm_sync_completed,
            button_bg_color,
            button_hover_color,
            width=16,   # Match width of Open Settings button
            font_size=12,
            text_color=button_text_color,
            disabled=True
        )
        
        # Extract button - full width in new row with accent color
        self.extract_button_frame = tk.Frame(self.button_grid_frame, bg=self.colors["bg_card"])
        self.extract_button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        self.extract_button = self.create_button(
            self.extract_button_frame,
            "3: EXTRACT MY PDFs",
            self.go_to_pdf_page,
            self.colors["extract"],
            "#a37b9a",  # Slightly darker than extract
            width=33,   # Full width button
            font_size=12,
            text_color=button_text_color,
            disabled=True
        )
        
        # Last sync time
        self.last_sync_var = tk.StringVar()
        self.last_sync_var.set(self.get_last_sync_time())
        
        self.last_sync_label = tk.Label(
            self.card_frame,
            textvariable=self.last_sync_var,
            font=("SF Pro Display", 11),
            fg=self.colors["text_dim"],
            bg=self.colors["bg_card"]
        )
        self.last_sync_label.pack(pady=15)
        
        # Footer
        self.footer_label = tk.Label(
            self.main_frame,
            text="Art Data Extract",
            font=("SF Pro Display", 10),
            fg=self.colors["text_dim"],
            bg=self.colors["bg_dark"]
        )
        self.footer_label.pack(side=tk.BOTTOM, pady=(15, 0))
        
        # Version
        self.version_label = tk.Label(
            self.main_frame,
            text="v2.2",
            font=("SF Pro Display", 9),
            fg=self.colors["text_dim"],
            bg=self.colors["bg_dark"]
        )
        self.version_label.pack(side=tk.BOTTOM, pady=(5, 0))
        
    def configure_styles(self):
        """Configure ttk styles"""
        self.style = ttk.Style()
        
        # Configure ttk styles if using any ttk widgets
        self.style.configure("TFrame", background=self.colors["bg_dark"])
        self.style.configure("TButton", 
                            font=("SF Pro Display", 12, "bold"),
                            background=self.colors["accent"])
        self.style.configure("TLabel", 
                            font=("SF Pro Display", 12),
                            background=self.colors["bg_dark"],
                            foreground=self.colors["text_light"])
    
    def create_step_frame(self, step_num, step_text, is_active=False):
        """Create a step indicator frame"""
        frame = tk.Frame(self.steps_indicator_frame, bg=self.colors["bg_card"])
        frame.pack(side=tk.LEFT, expand=True, padx=10)
        
        # Create colored circle with outer ring
        circle_size = 40
        circle_canvas = tk.Canvas(frame, width=circle_size, height=circle_size,
                                bg=self.colors["bg_card"], highlightthickness=0)
        circle_canvas.pack(pady=5)
        
        # Determine colors based on status
        if is_active:
            bg_color = self.colors["accent"]
            fg_color = self.colors["bg_dark"]
            ring_color = self.colors["accent"]
        else:
            bg_color = self.colors["bg_dark"]
            fg_color = self.colors["text_dim"]
            ring_color = self.colors["disabled"]
            
        # Draw outer ring
        circle_canvas.create_oval(1, 1, circle_size-1, circle_size-1, 
                                outline=ring_color, width=2, fill=bg_color)
        
        # Step number in circle
        circle_canvas.create_text(circle_size//2, circle_size//2, text=str(step_num),
                                fill=fg_color, font=("SF Pro Display", 16, "bold"))
        
        # Step text label
        step_label = tk.Label(frame, text=step_text, 
                             font=("SF Pro Display", 11),
                             fg=self.colors["text_dim"] if not is_active else self.colors["text_light"],
                             bg=self.colors["bg_card"])
        step_label.pack(pady=2)
        
        # Return a dictionary with all elements for later updating
        return {
            "frame": frame,
            "canvas": circle_canvas,
            "label": step_label,
            "active": is_active,
            "number": step_num,
            "text": step_text
        }
    
    def create_button(self, parent, text, command, bg_color, hover_color, disabled=False, width=30, font_size=13, text_color=None):
        """Create a styled button"""
        # Determine text color based on contrast need
        if text_color is None:
            text_color = self.colors["text_light"]
        
        button = tk.Button(
            parent,
            text=text,
            command=command,
            bg=bg_color,
            fg=text_color,
            font=("SF Pro Display", font_size, "bold"),
            width=width,
            relief=tk.FLAT,
            bd=0,
            padx=20,
            pady=12,
            activebackground=hover_color,
            activeforeground=text_color,
            cursor="hand2"
        )
        
        if disabled:
            button.config(state="disabled", bg=self.colors["disabled"], 
                         fg=self.colors["text_dim"])
        
        button.pack(pady=8)
        
        # Add hover effect
        button.bind("<Enter>", lambda e, btn=button, hc=hover_color: 
                    self.on_button_hover(btn, hc))
        button.bind("<Leave>", lambda e, btn=button, bc=bg_color: 
                    self.on_button_leave(btn, bc))
        
        return button
        
    def on_button_hover(self, button, hover_color):
        """Change button color on hover"""
        if button["state"] != "disabled":
            button.config(bg=hover_color)
    
    def on_button_leave(self, button, bg_color):
        """Restore button color when mouse leaves"""
        if button["state"] != "disabled":
            button.config(bg=bg_color)
            
    def update_step_indicator(self, current_step):
        """Update the step indicators to show progress"""
        for i, step_frame in enumerate(self.progress_frames):
            step_num = i + 1
            canvas = step_frame["canvas"]
            label = step_frame["label"]
            circle_size = 40
            
            # Clear canvas
            canvas.delete("all")
            
            if step_num < current_step:  # Completed step
                # Draw filled circle with checkmark
                canvas.create_oval(1, 1, circle_size-1, circle_size-1, 
                                  outline=self.colors["success"], width=2, 
                                  fill=self.colors["success"])
                # Draw checkmark
                canvas.create_text(circle_size//2, circle_size//2, text="✓",
                                  fill=self.colors["text_light"], 
                                  font=("SF Pro Display", 16, "bold"))
                label.config(fg=self.colors["success"])
                
            elif step_num == current_step:  # Current step
                # Draw active circle
                canvas.create_oval(1, 1, circle_size-1, circle_size-1, 
                                  outline=self.colors["accent"], width=2, 
                                  fill=self.colors["accent"])
                # Number
                canvas.create_text(circle_size//2, circle_size//2, text=str(step_num),
                                  fill=self.colors["bg_dark"], 
                                  font=("SF Pro Display", 16, "bold"))
                label.config(fg=self.colors["text_light"])
                
            else:  # Future step
                # Draw inactive circle
                canvas.create_oval(1, 1, circle_size-1, circle_size-1, 
                                  outline=self.colors["disabled"], width=2, 
                                  fill=self.colors["bg_dark"])
                # Number
                canvas.create_text(circle_size//2, circle_size//2, text=str(step_num),
                                  fill=self.colors["text_dim"], 
                                  font=("SF Pro Display", 16, "bold"))
                label.config(fg=self.colors["text_dim"])
    
    def get_last_sync_time(self):
        """Get the last sync time from log file"""
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync_log.json")
        
        try:
            if os.path.exists(log_path):
                with open(log_path, "r") as f:
                    data = json.load(f)
                    if "last_sync" in data:
                        return f"Last sync: {data['last_sync']}"
            return "Last sync: Never"
        except Exception:
            return "Last sync: Unknown"
    
    def confirm_sync_completed(self):
        """Handle sync confirmation"""
        # Update sync status
        self.sync_completed = True
        
        # Log the sync
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_sync_log({"last_sync": timestamp})
        
        # Update UI
        self.update_ui_for_completed_sync()
        
        # Show success message
        messagebox.showinfo("Sync Complete", 
                           "Sync confirmation successful! You can now extract your PDFs.")
    
    def update_ui_for_completed_sync(self):
        """Update UI after sync is confirmed"""
        # Update last sync time
        self.last_sync_var.set(self.get_last_sync_time())
        
        # Enable the extract button
        self.extract_button.config(
            state="normal", 
            bg=self.colors["extract"], 
            fg=self.colors["text_light"]
        )
        
        # Update step indicators
        self.update_step_indicator(3)
    
    def _save_sync_log(self, content):
        """Save sync log to file"""
        log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sync_log.json")
        
        try:
            with open(log_path, "w") as f:
                json.dump(content, f)
        except Exception as e:
            print(f"Error saving sync log: {e}")
    
    def open_message_preferences(self):
        """Open Messages preferences"""
        # Create a new thread to avoid blocking UI
        thread = threading.Thread(target=self._open_message_preferences_thread)
        thread.daemon = True
        thread.start()
        
        # Enable confirm button after a short delay
        self.root.after(1500, self._enable_confirm_button)
    
    def _enable_confirm_button(self):
        """Enable the confirm button after a delay"""
        self.confirm_button.config(
            state="normal", 
            bg=self.colors["secondary"], 
            fg=self.colors["text_light"]
        )
        # Update step indicators
        self.update_step_indicator(2)
    
    def _open_message_preferences_thread(self):
        """Thread to open Messages preferences"""
        try:
            # AppleScript to open Messages preferences
            script = '''
            tell application "Messages"
                activate
                tell application "System Events"
                    keystroke "," using command down
                    delay 0.5
                    tell application process "Messages"
                        try
                            click button "iMessage" of toolbar 1 of window 1
                        end try
                    end tell
                end tell
            end tell
            '''
            
            # Run the AppleScript
            subprocess.run(['osascript', '-e', script], check=True)
            
        except Exception as e:
            print(f"Error opening Messages preferences: {e}")
            # Show error message in main thread
            self.root.after(0, lambda: messagebox.showerror("Error", 
                f"Failed to open Messages preferences. Please try manually.\n\nError: {str(e)}"))
    
    def go_to_pdf_page(self):
        """Open PDF extractor"""
        try:
            # Get the directory of this script
            script_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Look for PDF extractor script
            pdf_script = os.path.join(script_dir, "imessage_pdf_extract_gui.py")
            
            if os.path.exists(pdf_script):
                # Run the PDF extractor
                subprocess.Popen(['python3', pdf_script])
                self.root.destroy()  # Close current window
            else:
                # Check for alternate script names
                alternate_scripts = [
                    "pdf_extractor.py",
                    "imessage_pdf_extract.py",
                    "launch_pdf_extractor.command"
                ]
                
                for script in alternate_scripts:
                    script_path = os.path.join(script_dir, script)
                    if os.path.exists(script_path):
                        if script.endswith('.command'):
                            # Run command file
                            subprocess.Popen(['open', script_path])
                        else:
                            # Run Python script
                            subprocess.Popen(['python3', script_path])
                        self.root.destroy()  # Close current window
                        return
                
                # If no script found, show error
                messagebox.showerror("Error", "PDF extraction script not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open PDF extractor: {str(e)}")

def main():
    root = tk.Tk()
    app = MessagesSyncApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
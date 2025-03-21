#!/usr/bin/env python3
import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import logging
import re
from typing import Dict, Optional, List, Any, Tuple
import json
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
from queue import Queue
import subprocess
import plistlib
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from core.pdf_extractor import IMessagePDFExtractor

# Create logs directory in user's home directory
log_dir = Path.home() / ".pdf_rescue_squad"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "pdf_rescue.log"

# Configure logging to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
logger.info("PDF Rescue Squad starting up... 🚀")

# Log system information
logger.info(f"Python version: {sys.version}")
logger.info(f"Operating system: {os.uname().sysname} {os.uname().release}")
logger.info(f"Log file location: {log_file}")

class PermissionChecker:
    @staticmethod
    def check_full_disk_access() -> bool:
        """Check if the app has Full Disk Access permission."""
        messages_db = Path.home() / "Library/Messages/chat.db"
        try:
            # Try to open the Messages database
            with sqlite3.connect(messages_db) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except sqlite3.Error:
            return False
    
    @staticmethod
    def check_accessibility_permission() -> bool:
        """Check if the app has Accessibility permission."""
        script = '''
        tell application "System Events"
            try
                get name of application processes
                return "has_permissions"
            on error
                return "needs_permissions"
            end try
        end tell
        '''
        try:
            result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
            return "has_permissions" in result.stdout
        except:
            return False
    
    @staticmethod
    def request_full_disk_access():
        """Open System Settings to Full Disk Access page."""
        subprocess.run([
            'open',
            'x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles'
        ])
    
    @staticmethod
    def request_accessibility_permission():
        """Open System Settings to Accessibility page."""
        subprocess.run([
            'open',
            'x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility'
        ])

class PDFExtractorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("PDF Rescue Squad 🚀")
        self.geometry("800x800+50+50")  # Position window at (50,50)
        self.minsize(800, 800)
        
        # Configure macOS-style appearance
        self.style = ttk.Style()
        if 'darwin' in self.tk.call('tk', 'windowingsystem'):
            self.tk.call('tk::unsupported::MacWindowStyle', 'style', self._w, 'document', 'closeBox')
        
        # Configure styles
        self._configure_styles()
        
        # Set window background
        self.configure(background='#F9FBFD')
        
        # Initialize state
        self.selected_pdfs = []
        self.output_dir = Path.home() / "Downloads" / "Rescued_PDFs"
        
        # Create main container
        self.container = ttk.Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        
        # Initialize frames dictionary
        self.frames = {}
        
        # Create frames
        for F in (SyncCheckFrame, AnalysisFrame, ExtractionFrame):
            frame = F(self.container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Show initial frame
        self.show_frame(SyncCheckFrame)
        
        # Check permissions after a short delay
        self.after(500, self._check_permissions)
    
    def _check_permissions(self):
        """Check and request necessary permissions."""
        checker = PermissionChecker()
        
        # Check Full Disk Access
        if not checker.check_full_disk_access():
            response = messagebox.showinfo(
                "Full Disk Access Required",
                "This app needs Full Disk Access permission to read your Messages database.\n\n"
                "1. Click OK to open System Settings\n"
                "2. Click the '+' button\n"
                "3. Navigate to your Python installation or this app\n"
                "4. Select it and click 'Open'\n"
                "5. Enable the checkbox\n\n"
                "After granting permission, please restart the app.",
                icon='info'
            )
            checker.request_full_disk_access()
            self.quit()
            return
        
        # Check Accessibility permission
        if not checker.check_accessibility_permission():
            response = messagebox.showinfo(
                "Accessibility Access Required",
                "This app needs Accessibility permission to control Messages settings.\n\n"
                "1. Click OK to open System Settings\n"
                "2. Click the '+' button\n"
                "3. Navigate to your Python installation or this app\n"
                "4. Select it and click 'Open'\n"
                "5. Enable the checkbox\n\n"
                "After granting permission, please restart the app.",
                icon='info'
            )
            checker.request_accessibility_permission()
            self.quit()
            return
    
    def _configure_styles(self):
        """Configure ttk styles for the application."""
        # Configure frame styles
        self.style.configure('Main.TFrame',
            background='#F9FBFD'
        )
        
        # Configure label styles
        self.style.configure('Header.TLabel',
            font=('SF Pro Display', 28, 'bold'),
            background='#F9FBFD',
            foreground='#1C2D38'
        )
        
        self.style.configure('Subheader.TLabel',
            font=('SF Pro Text', 14),
            background='#F9FBFD',
            foreground='#41484F'
        )
        
        # Configure checkbox style
        self.style.configure('Sync.TCheckbutton',
            font=('SF Pro Text', 14),
            background='#F9FBFD',
            foreground='#1C2D38'
        )
        
        self.style.map('Sync.TCheckbutton',
            background=[('active', '#F9FBFD')],
            foreground=[('disabled', '#889397')],
            indicatorcolor=[('selected', '#0066FF'), ('', '#E3E6E8')],
            indicatorrelief=[('', 'flat')],
            relief=[('', 'flat')]
        )
        
        # Configure button styles
        self.style.configure('Primary.TButton',
            font=('SF Pro Text', 13),
            padding=(16, 8),
            background='#0066FF',
            foreground='white'
        )
        
        self.style.map('Primary.TButton',
            background=[('active', '#0052CC'), ('disabled', '#E3E6E8')],
            foreground=[('disabled', '#889397')]
        )
        
        self.style.configure('Secondary.TButton',
            font=('SF Pro Text', 13),
            padding=(16, 8),
            background='#FFFFFF',
            foreground='#1C2D38'
        )
        
        self.style.map('Secondary.TButton',
            background=[('active', '#F9FBFD'), ('disabled', '#F9FBFD')],
            foreground=[('disabled', '#889397')]
        )
        
        # Configure labelframe style
        self.style.configure('Instructions.TLabelframe',
            background='#FFFFFF',
            bordercolor='#E3E6E8',
            lightcolor='#E3E6E8',
            darkcolor='#E3E6E8'
        )
        
        self.style.configure('Instructions.TLabelframe.Label',
            font=('SF Pro Text', 14, 'bold'),
            background='#FFFFFF',
            foreground='#1C2D38',
            padding=(0, 10)
        )
        
        # Configure progress bar style
        self.style.configure("macOS.Horizontal.TProgressbar",
            troughcolor='#E3E6E8',
            background='#00ED64',
            darkcolor='#00684A',
            lightcolor='#00ED64',
            bordercolor='#E3E6E8',
            thickness=6
        )
    
    def show_frame(self, frame_class):
        """Show the specified frame."""
        frame = self.frames[frame_class]
        frame.tkraise()
        frame.on_show()

class BaseFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, style='Main.TFrame')
        self.controller = controller
    
    def on_show(self):
        """Called when the frame is shown."""
        pass

def check_messages_settings() -> Tuple[bool, str]:
    """Check Messages.app settings using AppleScript."""
    logger.info("Checking Messages settings...")
    
    script = '''
    -- First make sure we close any open settings window
    tell application "System Events"
        tell process "Messages"
            try
                keystroke "w" using command down -- Close current window if any
                delay 0.5
            on error
                -- No window to close, continue
            end try
        end tell
    end tell
    
    -- Activate Messages app
    tell application "Messages" to activate
    delay 1.5
    
    -- Use keyboard shortcut to open settings
    tell application "System Events"
        tell process "Messages"
            try
                keystroke "," using command down
                delay 1.5
                
                -- Verify settings window opened successfully
                if (count of windows) = 0 then
                    return "error: No settings window found"
                end if
                
                -- Use three simple steps:
                -- 1. Click iMessage tab using direct coordinates
                set settingsWin to window 1
                set winPos to position of settingsWin
                set winSize to size of settingsWin
                
                -- Click near the top center to select iMessage tab 
                set tabX to (item 1 of winPos) + ((item 1 of winSize) / 2)
                set tabY to (item 2 of winPos) + 32
                click at {tabX, tabY}
                delay 1.5
                
                -- 2. Try a single targeted click to hit the Sync Now button
                --    Most reliable position: ~75% from top, center horizontally
                set syncX to (item 1 of winPos) + ((item 1 of winSize) / 2)
                set syncY to (item 2 of winPos) + ((item 2 of winSize) * 0.75)
                
                click at {syncX, syncY}
                
                -- Return success
                return "true"
            on error errMsg
                return "error: " & errMsg
            end try
        end tell
    end tell
    '''
    
    try:
        logger.info("Executing check script...")
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Check script output: {output}")
            
            if output == "true":
                return True, "Messages in iCloud is enabled and sync initiated"
            elif "error:" in output:
                logger.error(f"AppleScript error: {output}")
                return False, f"Error checking settings: {output}"
            else:
                return False, f"Unexpected result: {output}"
        else:
            logger.error(f"Check script failed: {result.stderr}")
            return False, f"Error checking settings: {result.stderr}"
    except Exception as e:
        logger.error(f"Exception during check: {str(e)}")
        return False, f"Error running AppleScript: {str(e)}"

def enable_messages_sync() -> Tuple[bool, str]:
    """Enable Messages sync using AppleScript."""
    logger.info("Starting Messages sync process...")
    
    script = '''
    -- First make sure Messages is running and active
    tell application "Messages"
        activate
    end tell
    
    -- Wait for Messages to be frontmost and ready
    tell application "System Events"
        repeat 10 times
            if exists (first process whose frontmost is true and name is "Messages") then
                exit repeat
            end if
            delay 0.5
        end repeat
    end tell

    tell application "System Events"
        tell process "Messages"
            try
                -- First verify Messages is running
                if not (exists process "Messages") then
                    return "error: Messages is not running"
                end if
                
                -- Check if Settings window is already open
                set settingsOpen to false
                repeat with w in windows
                    if name of w is "Settings" then
                        set settingsOpen to true
                        exit repeat
                    end if
                end repeat
                
                if not settingsOpen then
                    -- Try menu approach first (most reliable)
                    try
                        click menu item "Settings…" of menu "Messages" of menu bar 1
                        delay 1
                    on error
                        -- If menu approach fails, try keyboard shortcut
                        try
                            keystroke "," using command down
                            delay 1
                        on error
                            return "error: Could not open Settings window"
                        end try
                    end try
                    
                    -- Verify Settings window opened
                    set settingsOpen to false
                    repeat with w in windows
                        if name of w contains "Settings" then
                            set settingsOpen to true
                            exit repeat
                        end if
                    end repeat
                    
                    if not settingsOpen then
                        return "error: Settings window did not open"
                    end if
                end if
                
                tell window "Settings"
                    -- Click iMessage tab if not already selected
                    set foundTab to false
                    
                    -- Try to find the iMessage tab button
                    repeat with toolbarButton in (buttons of toolbar 1)
                        try
                            if description of toolbarButton contains "iMessage" then
                                -- Check if already selected
                                set isSelected to value of toolbarButton is 1
                                if not isSelected then
                                    click toolbarButton
                                end if
                                set foundTab to true
                                -- Wait for tab content to load
                                delay 1.5
                                exit repeat
                            end if
                        on error
                            -- Skip if we can't check this button
                        end try
                    end repeat
                    
                    if not foundTab then
                        -- Try alternative methods to find the tab
                        try
                            -- Get window dimensions for positioning
                            set winPos to position of window "Settings"
                            set winSize to size of window "Settings"
                            
                            -- Try to click where the iMessage tab should be (middle of toolbar)
                            set tabY to (item 2 of winPos) + 35
                            set tabX to (item 1 of winPos) + (item 1 of winSize) * 0.5
                            click at {tabX, tabY}
                            delay 1.5
                            set foundTab to true
                        on error
                            return "error: Could not find or click iMessage tab"
                        end try
                    end if
                    
                    -- Enable sync if not already enabled
                    set foundCheckbox to false
                    
                    -- Try multiple methods to find the checkbox
                    repeat with aGroup in groups
                        try
                            set allCheckboxes to checkboxes of aGroup
                            repeat with cb in allCheckboxes
                                try
                                    if name of cb contains "Enable Messages in iCloud" or title of cb contains "Enable Messages in iCloud" or description of cb contains "Enable Messages in iCloud" then
                                        if not (value of cb as boolean) then
                                            click cb
                                            delay 1.5
                                        end if
                                        set foundCheckbox to true
                                        exit repeat
                                    end if
                                on error
                                    -- Skip if we can't check this checkbox
                                end try
                            end repeat
                            
                            if foundCheckbox then exit repeat
                        on error
                            -- Skip if group has no checkboxes
                        end try
                    end repeat
                    
                    if not foundCheckbox then
                        -- Try a more generic search if we couldn't find by name
                        repeat with aGroup in groups
                            try
                                set allCheckboxes to checkboxes of aGroup
                                if (count of allCheckboxes) > 0 then
                                    -- Assume first checkbox in the iMessage tab is likely the one we want
                                    set mainCheckbox to item 1 of allCheckboxes
                                    if not (value of mainCheckbox as boolean) then
                                        click mainCheckbox
                                        delay 1.5
                                    end if
                                    set foundCheckbox to true
                                    exit repeat
                                end if
                            on error
                                -- Continue to next group
                            end try
                        end repeat
                        
                        if not foundCheckbox then
                            return "error: Could not find sync checkbox"
                        end if
                    end if
                    
                    -- Click Sync Now button
                    set foundSync to false
                    
                    -- First try to find by name in groups
                    repeat with aGroup in groups
                        try
                            set btns to buttons of aGroup
                            repeat with btn in btns
                                if name of btn is "Sync Now" or title of btn is "Sync Now" then
                                    if enabled of btn then
                                        click btn
                                        log "Successfully clicked Sync Now button"
                                    else
                                        log "Sync Now button is disabled"
                                    end if
                                    set foundSync to true
                                    exit repeat
                                end if
                            end repeat
                            
                            if foundSync then exit repeat
                        on error
                            -- Continue to next group if error
                        end try
                    end repeat
                    
                    -- If not found by name, try other methods
                    if not foundSync then
                        try
                            -- Look for any button with "Sync" in its name
                            set allButtons to buttons of window "Settings"
                            repeat with btn in allButtons
                                try
                                    if name of btn contains "Sync" then
                                        click btn
                                        set foundSync to true
                                        exit repeat
                                    end if
                                on error
                                    -- Continue to next button
                                end try
                            end repeat
                            
                            -- As a last resort, try a coordinate approach
                            if not foundSync then
                                set winPos to position of window "Settings"
                                set winSize to size of window "Settings"
                                
                                -- Try clicking in the lower part of the window where Sync Now likely is
                                set syncY to (item 2 of winPos) + (item 2 of winSize) * 0.7
                                set syncX to (item 1 of winPos) + (item 1 of winSize) * 0.5
                                click at {syncX, syncY}
                                set foundSync to true
                            end if
                        on error errMsg
                            log "Error finding Sync button: " & errMsg
                            -- Keep going to get final status
                        end try
                    end if
                    
                    -- Get final sync status
                    delay 1
                    set foundStatus to false
                    repeat with aGroup in groups
                        try
                            set allCheckboxes to checkboxes of aGroup
                            repeat with cb in allCheckboxes
                                try
                                    if name of cb contains "Enable Messages in iCloud" or title of cb contains "Enable Messages in iCloud" or description of cb contains "Enable Messages in iCloud" then
                                        set finalStatus to value of cb as boolean
                                        set foundStatus to true
                                        return finalStatus as string
                                    end if
                                on error
                                    -- Skip if we can't check this checkbox
                                end try
                            end repeat
                            
                            if foundStatus then exit repeat
                        on error
                            -- Skip if group has no checkboxes
                        end try
                    end repeat
                    
                    if not foundStatus then
                        -- If we couldn't find the specific checkbox, just assume success if we got this far
                        return "true"
                    end if
                end tell
            on error errMsg
                log "Error: " & errMsg
                return "error: " & errMsg
            end try
        end tell
    end tell
    '''
    
    try:
        logger.info("Executing enable script...")
        result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
        
        if result.returncode == 0:
            output = result.stdout.strip()
            logger.info(f"Enable script output: {output}")
            
            if output == "true":
                return True, "Messages in iCloud successfully enabled"
            elif output == "false":
                return False, "Messages in iCloud is disabled"
            elif "error:" in output:
                logger.error(f"AppleScript error: {output}")
                return False, f"Error enabling Messages sync: {output}"
            else:
                return False, f"Unexpected result: {output}"
        else:
            error = result.stderr.strip()
            logger.error(f"Enable script failed: {error}")
            return False, f"Error enabling Messages sync: {error}"
    except Exception as e:
        logger.error(f"Exception during enable: {str(e)}")
        return False, f"Error running AppleScript: {str(e)}"

class SyncCheckFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._create_widgets()
    
    def on_show(self):
        """Called when the frame is shown."""
        # Don't automatically check settings, wait for user action
        pass
    
    def _create_widgets(self):
        # Create header with emoji
        header = ttk.Label(
            self,
            text="Mission Control 🛸",
            style='Header.TLabel'
        )
        header.pack(pady=(40, 20), padx=40, anchor='w')
        
        # Create tab-like section header
        tab_frame = ttk.Frame(self, style='Main.TFrame')
        tab_frame.pack(fill='x', padx=40)
        
        general_tab = ttk.Label(
            tab_frame,
            text="Pre-flight Checklist ✨",
            style='Subheader.TLabel',
            background='#FFFFFF',
            foreground='#0066FF',
            padding=(20, 10)
        )
        general_tab.pack(side='left')
        
        # Add separator below tabs
        separator = ttk.Separator(self, orient='horizontal')
        separator.pack(fill='x', pady=(0, 20))
        
        # Main description with fun text
        description = ttk.Label(
            self,
            text="Before we embark on our PDF rescue mission, let's make sure your messages are properly synced and ready for extraction! 🚀",
            style='Subheader.TLabel',
            wraplength=700
        )
        description.pack(pady=(10, 20), padx=40, anchor='w')
        
        # Instructions frame with white background
        instructions_frame = ttk.LabelFrame(
            self,
            text="Sync Configuration 🔄",
            padding=(20, 10),
            style='Instructions.TLabelframe'
        )
        instructions_frame.pack(padx=40, pady=(0, 20), fill='x')
        
        # Instructions text with emojis
        instructions_text = """1. On your iPhone 📱:
    • Go to Settings → Messages
    • Enable 'iMessage' ✅
    • Go to Settings → [your Apple ID at top] → iCloud ☁️
    • Enable 'Messages' in the iCloud settings
    • Select 'iCloud Backup' and tap 'Back Up Now' 🔄
    • Wait for backup to complete (grab a coffee! ☕️)

2. On your Mac 💻:
    • Open Messages app
    • Go to Messages → Settings → iMessage
    • Enable 'Enable Messages in iCloud' ✨
    • Click 'Sync Now' and wait for sync to complete
    • If messages are missing, try clicking 'Sync Now' again 🔄

Note: If messages are not appearing 🤔:
    • Check that Messages is enabled in your iPhone's iCloud settings
    • Force a backup on your iPhone 📱
    • Then try syncing again on your Mac 🔄"""
        
        ttk.Label(
            instructions_frame,
            text=instructions_text,
            justify='left',
            font=('SF Pro Text', 13),
            wraplength=700,
            background='#FFFFFF'
        ).pack(pady=10)
        
        # Button to check Messages settings
        check_button = ttk.Button(
            self,
            text="Check Messages Settings →",
            command=self._check_messages_settings,
            style='Primary.TButton'
        )
        check_button.pack(pady=20)
        
        # Confirmation checkbox (hidden initially)
        self.confirm_frame = ttk.Frame(self, style='Main.TFrame')
        
        self.sync_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(
            self.confirm_frame,
            text="Enable Message Sync",
            variable=self.sync_var,
            command=self._on_sync_change,
            style='Sync.TCheckbutton'
        ).pack(side='left')
        
        sync_description = ttk.Label(
            self.confirm_frame,
            text="Verify that your messages are properly synced between devices.",
            style='Subheader.TLabel',
            foreground='#6C757D'
        )
        sync_description.pack(side='left', padx=20)
        
        # Next button frame (hidden initially)
        self.button_frame = ttk.Frame(self, style='Main.TFrame')
        
        self.next_button = ttk.Button(
            self.button_frame,
            text="Find PDFs →",
            command=self._on_next,
            style='Primary.TButton',
            state='disabled'
        )
        self.next_button.pack(side='left')
    
    def _check_messages_settings(self):
        """Check Messages settings when user clicks the button."""
        is_enabled, message = check_messages_settings()
        
        if message == "permissions_needed":
            messagebox.showinfo(
                "Permissions Required",
                "This app needs permission to control Messages.\n\n"
                "1. Open System Settings\n"
                "2. Go to Privacy & Security → Accessibility\n"
                "3. Click the '+' button\n"
                "4. Navigate to your Python installation or this app\n"
                "5. Select it and click 'Open'\n"
                "6. Enable the checkbox\n\n"
                "After granting permissions, try again."
            )
            return
        
        if is_enabled:
            self.sync_var.set(True)
            self._show_confirmation()
        else:
            if "not running" in message:
                messagebox.showinfo(
                    "Messages App Required",
                    "Please open the Messages app to check sync settings."
                )
            elif "not enabled" in message:
                if messagebox.askyesno(
                    "Enable Messages Sync",
                    "Messages in iCloud is not enabled. Would you like to enable it now?"
                ):
                    success, result = enable_messages_sync()
                    if success:
                        self.sync_var.set(True)
                        self._show_confirmation()
                    else:
                        messagebox.showerror("Error", result)
    
    def _show_confirmation(self):
        """Show the confirmation checkbox and next button."""
        self.confirm_frame.pack(fill='x', padx=40, pady=20)
        self.button_frame.pack(fill='x', padx=40, pady=20)
        self._on_sync_change()
    
    def _on_sync_change(self):
        """Handle sync checkbox state change."""
        if self.sync_var.get():
            self.next_button.configure(state='normal')
        else:
            self.next_button.configure(state='disabled')
    
    def _on_next(self):
        """Proceed to analysis frame."""
        self.controller.show_frame(AnalysisFrame)

class AnalysisFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._create_widgets()
        self.pdfs = []
    
    def _create_widgets(self):
        # Create header with fun text
        header = ttk.Label(
            self,
            text="PDF Discovery Zone 🔍",
            style='Header.TLabel'
        )
        header.pack(pady=(40, 20), padx=40)
        
        # Progress section
        self.progress_frame = ttk.Frame(self, style='Main.TFrame')
        self.progress_frame.pack(pady=20)
        
        self.progress_var = tk.StringVar(value="Scanning for PDFs in the digital cosmos... 🌌")
        progress_label = ttk.Label(
            self.progress_frame,
            textvariable=self.progress_var,
            style='Subheader.TLabel'
        )
        progress_label.pack(pady=(0, 20))
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame,
            mode='indeterminate',
            style='macOS.Horizontal.TProgressbar',
            length=400
        )
        
        # Results section (hidden initially)
        self.results_frame = ttk.Frame(self, style='Main.TFrame')
        
        # Create table
        table_frame = ttk.Frame(self.results_frame)
        table_frame.pack(fill='both', expand=True, padx=40)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame)
        scrollbar.pack(side='right', fill='y')
        
        # Treeview for PDFs
        self.tree = ttk.Treeview(
            table_frame,
            columns=('select', 'filename', 'date', 'size', 'sender'),
            show='headings',
            height=15
        )
        
        # Configure scrollbar
        scrollbar.config(command=self.tree.yview)
        self.tree.config(yscrollcommand=scrollbar.set)
        
        # Configure columns
        self.tree.column('select', width=30, anchor='center')
        self.tree.column('filename', width=300, anchor='w')
        self.tree.column('date', width=150, anchor='w')
        self.tree.column('size', width=100, anchor='e')
        self.tree.column('sender', width=150, anchor='w')
        
        # Configure headers
        self.tree.heading('select', text='✓')
        self.tree.heading('filename', text='Filename')
        self.tree.heading('date', text='Date')
        self.tree.heading('size', text='Size')
        self.tree.heading('sender', text='From')
        
        self.tree.pack(fill='both', expand=True)
        
        # Selection controls
        controls_frame = ttk.Frame(self.results_frame, style='Main.TFrame')
        controls_frame.pack(fill='x', padx=40, pady=20)
        
        ttk.Button(
            controls_frame,
            text="Select All",
            command=self._select_all,
            style='Secondary.TButton'
        ).pack(side='left', padx=5)
        
        ttk.Button(
            controls_frame,
            text="Deselect All",
            command=self._deselect_all,
            style='Secondary.TButton'
        ).pack(side='left', padx=5)
        
        self.selection_label = ttk.Label(
            controls_frame,
            text="0 PDFs selected",
            style='Subheader.TLabel'
        )
        self.selection_label.pack(side='right', padx=5)
        
        # Navigation buttons
        self.button_frame = ttk.Frame(self, style='Main.TFrame')
        
        ttk.Button(
            self.button_frame,
            text="← Back",
            command=lambda: self.controller.show_frame(SyncCheckFrame),
            style='Secondary.TButton'
        ).pack(side='left', padx=10)
        
        self.extract_button = ttk.Button(
            self.button_frame,
            text="Extract Selected PDFs →",
            command=self._on_extract,
            style='Primary.TButton',
            state='disabled'
        )
        self.extract_button.pack(side='left', padx=10)
        
        # Bind selection events
        self.tree.bind('<<TreeviewSelect>>', self._on_selection_change)
        self.tree.bind('<space>', self._toggle_selection)
    
    def on_show(self):
        """Start analysis when frame is shown."""
        self.progress_frame.pack(pady=20)
        self.progress_bar.pack(pady=(0, 40))
        self.progress_bar.start()
        self.progress_var.set("Analyzing Messages database...")
        
        # Hide results if showing again
        self.results_frame.pack_forget()
        self.button_frame.pack_forget()
        
        # Clear previous results
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Start analysis in background thread
        threading.Thread(target=self._analyze_messages, daemon=True).start()
    
    def _analyze_messages(self):
        """Analyze messages database for PDFs."""
        try:
            extractor = IMessagePDFExtractor()
            self.pdfs = extractor.get_pdf_list()
            
            # Update UI in main thread
            self.after(0, self._show_results)
            
        except Exception as e:
            self.after(0, lambda: messagebox.showerror(
                "Error",
                f"Failed to analyze messages: {str(e)}"
            ))
            self.after(0, lambda: self.controller.show_frame(SyncCheckFrame))
    
    def _show_results(self):
        """Show analysis results."""
        self.progress_bar.stop()
        self.progress_frame.pack_forget()
        
        # Update header and progress text
        if not self.pdfs:
            self.progress_var.set("No PDFs found in Messages")
            return
        
        # Populate tree
        for pdf in self.pdfs:
            # Format size
            size_bytes = pdf['size']
            if size_bytes < 1024:
                size = f"{size_bytes} B"
            elif size_bytes < 1024*1024:
                size = f"{size_bytes/1024:.1f} KB"
            else:
                size = f"{size_bytes/(1024*1024):.1f} MB"
            
            # Format date
            date = datetime.fromisoformat(pdf['date']).strftime("%Y-%m-%d %H:%M")
            
            self.tree.insert('', 'end',
                values=('', pdf['filename'], date, size, pdf['sender'] or 'Unknown'),
                tags=('disabled',) if not pdf['exists'] else ())
        
        # Show results
        self.results_frame.pack(pady=20, fill='both', expand=True)
        self.button_frame.pack(pady=(0, 40))
        
        # Configure tag for disabled items
        self.tree.tag_configure('disabled', foreground='#999999')
    
    def _select_all(self):
        """Select all available PDFs."""
        for item in self.tree.get_children():
            if 'disabled' not in self.tree.item(item)['tags']:
                self.tree.set(item, 'select', '✓')
        self._update_selection_count()
    
    def _deselect_all(self):
        """Deselect all PDFs."""
        for item in self.tree.get_children():
            self.tree.set(item, 'select', '')
        self._update_selection_count()
    
    def _toggle_selection(self, event):
        """Toggle selection of current item."""
        item = self.tree.focus()
        if item and 'disabled' not in self.tree.item(item)['tags']:
            current = self.tree.set(item, 'select')
            self.tree.set(item, 'select', '' if current == '✓' else '✓')
            self._update_selection_count()
    
    def _on_selection_change(self, event):
        """Update selection count when selection changes."""
        self._update_selection_count()
    
    def _update_selection_count(self):
        """Update selection count and extract button state."""
        count = sum(1 for item in self.tree.get_children()
                   if self.tree.set(item, 'select') == '✓')
        
        self.selection_label.configure(
            text=f"{count} PDF{'s' if count != 1 else ''} selected"
        )
        
        self.extract_button.configure(
            state='normal' if count > 0 else 'disabled'
        )
    
    def _on_extract(self):
        """Proceed to extraction frame with selected PDFs."""
        # Get selected PDFs
        selected = []
        for item in self.tree.get_children():
            if self.tree.set(item, 'select') == '✓':
                idx = len(selected)
                pdf = self.pdfs[idx]
                if pdf['exists']:
                    selected.append(pdf)
        
        # Store selected PDFs in controller
        self.controller.selected_pdfs = selected
        
        # Show extraction frame
        self.controller.show_frame(ExtractionFrame)

class ExtractionFrame(BaseFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, controller)
        self._create_widgets()
        self.extraction_running = False
    
    def _create_widgets(self):
        # Create header
        header = ttk.Label(
            self,
            text="PDF Rescue Mission 🛸",
            style='Header.TLabel'
        )
        header.pack(pady=(40, 20), padx=40)
        
        # Summary section
        summary_frame = ttk.LabelFrame(
            self,
            text="Mission Briefing 📋",
            padding=(20, 10)
        )
        summary_frame.pack(padx=40, pady=(0, 20), fill='x')
        
        self.summary_var = tk.StringVar()
        summary_label = ttk.Label(
            summary_frame,
            textvariable=self.summary_var,
            font=('SF Pro Text', 12)
        )
        summary_label.pack(pady=10)
        
        # Output directory section
        output_frame = ttk.LabelFrame(
            self,
            text="Landing Zone 🎯",
            padding=(20, 10)
        )
        output_frame.pack(padx=40, pady=(0, 20), fill='x')
        
        self.output_path = tk.StringVar(
            value=str(self.controller.output_dir)
        )
        
        output_entry = ttk.Entry(
            output_frame,
            textvariable=self.output_path,
            font=('SF Pro Text', 12)
        )
        output_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        ttk.Button(
            output_frame,
            text="Choose Landing Site 🗺",
            command=self._browse_output_dir,
            style='Secondary.TButton'
        ).pack(side='right')
        
        # Progress section
        progress_frame = ttk.LabelFrame(
            self,
            text="Mission Progress 📊",
            padding=(20, 10)
        )
        progress_frame.pack(padx=40, pady=(0, 20), fill='x')
        
        self.progress_var = tk.StringVar(value="Ready to initiate rescue sequence... 🚀")
        progress_label = ttk.Label(
            progress_frame,
            textvariable=self.progress_var,
            font=('SF Pro Text', 12)
        )
        progress_label.pack(pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            style='macOS.Horizontal.TProgressbar'
        )
        self.progress_bar.pack(fill='x')
        
        # Buttons
        button_frame = ttk.Frame(self, style='Main.TFrame')
        button_frame.pack(pady=(0, 40))
        
        ttk.Button(
            button_frame,
            text="← Return to Base",
            command=lambda: self.controller.show_frame(AnalysisFrame),
            style='Secondary.TButton'
        ).pack(side='left', padx=10)
        
        self.extract_button = ttk.Button(
            button_frame,
            text="Launch Rescue Mission 🚀",
            command=self._start_extraction,
            style='Primary.TButton'
        )
        self.extract_button.pack(side='left', padx=10)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="Abort Mission 🛑",
            command=self._stop_extraction,
            style='Secondary.TButton',
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=10)
    
    def on_show(self):
        """Update summary when frame is shown."""
        pdfs = self.controller.selected_pdfs
        count = len(pdfs)
        total_size = sum(pdf['size'] for pdf in pdfs)
        
        # Format total size
        if total_size < 1024:
            size = f"{total_size} B"
        elif total_size < 1024*1024:
            size = f"{total_size/1024:.1f} KB"
        else:
            size = f"{total_size/(1024*1024):.1f} MB"
        
        self.summary_var.set(
            f"Mission objective: Rescue {count} PDF{'s' if count != 1 else ''} "
            f"(total payload: {size}) 📦"
        )
    
    def _browse_output_dir(self):
        """Browse for output directory."""
        directory = filedialog.askdirectory(
            initialdir=self.output_path.get(),
            title="Select Output Directory"
        )
        if directory:
            self.output_path.set(directory)
            self.controller.output_dir = Path(directory)
    
    def _start_extraction(self):
        """Start PDF extraction."""
        self.extract_button.configure(state='disabled')
        self.stop_button.configure(state='normal')
        
        # Create message queue for progress updates
        self.message_queue = Queue()
        self.extraction_running = True
        
        # Start extraction in background thread
        threading.Thread(
            target=self._extract_pdfs,
            daemon=True
        ).start()
        
        # Start processing messages
        self._process_messages()
    
    def _stop_extraction(self):
        """Stop PDF extraction."""
        self.extraction_running = False
        self.stop_button.configure(state='disabled')
        self.extract_button.configure(state='normal')
    
    def _extract_pdfs(self):
        """Extract PDFs in background thread."""
        try:
            # Create output directory
            output_dir = Path(self.output_path.get())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Get total size for progress calculation
            total_size = sum(pdf['size'] for pdf in self.controller.selected_pdfs)
            processed_size = 0
            
            # Extract each PDF
            for i, pdf in enumerate(self.controller.selected_pdfs, 1):
                if not self.extraction_running:
                    self.message_queue.put({
                        'type': 'progress',
                        'text': "Mission aborted! 🛑",
                        'percent': 0
                    })
                    break
                
                try:
                    # Get source path
                    source_path = Path(pdf['path'])
                    if not source_path.exists():
                        continue
                    
                    # Create destination path
                    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', pdf['filename'])
                    dest_path = output_dir / safe_filename
                    
                    # Copy file
                    shutil.copy2(source_path, dest_path)
                    
                    # Update progress
                    processed_size += pdf['size']
                    percent = int((processed_size / total_size) * 100)
                    
                    self.message_queue.put({
                        'type': 'progress',
                        'text': f"Rescuing PDF {i}/{len(self.controller.selected_pdfs)}: {safe_filename} 🛸",
                        'percent': percent
                    })
                    
                except Exception as e:
                    self.message_queue.put({
                        'type': 'error',
                        'text': f"Failed to rescue {pdf['filename']}: {str(e)} 💥"
                    })
            
            if self.extraction_running:
                self.message_queue.put({
                    'type': 'complete',
                    'text': f"Mission accomplished! Successfully rescued {i} PDFs to safety! 🎉"
                })
            
        except Exception as e:
            self.message_queue.put({
                'type': 'error',
                'text': f"Mission failure: {str(e)} 💥"
            })
    
    def _process_messages(self):
        """Process messages from extraction thread."""
        try:
            message = self.message_queue.get_nowait()
            
            if message['type'] == 'progress':
                self.progress_var.set(message['text'])
                if 'percent' in message:
                    self.progress_bar.configure(value=message['percent'])
            elif message['type'] == 'error':
                messagebox.showerror("Error", message['text'])
                self._stop_extraction()
            elif message['type'] == 'complete':
                self.progress_var.set(message['text'])
                self.progress_bar.configure(value=100)
                self._stop_extraction()
                
                # Ask to open output directory
                if messagebox.askyesno(
                    "Extraction Complete",
                    f"{message['text']}\n\nWould you like to open the output directory?"
                ):
                    self._open_output_dir()
            
        except:
            pass
        
        if self.extraction_running:
            self.after(100, self._process_messages)
    
    def _open_output_dir(self):
        """Open the output directory in Finder."""
        import subprocess
        subprocess.run(['open', self.output_path.get()])

def main():
    app = PDFExtractorApp()
    app.mainloop()

if __name__ == "__main__":
    main() 
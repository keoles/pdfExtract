#!/usr/bin/env python3
import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import logging
import re
from typing import Dict, Optional, List, Any
import json
from queue import Queue

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IMessagePDFExtractor:
    def __init__(self, output_dir: str = "extracted_pdfs", skip_validation: bool = False, message_queue: Queue = None):
        self.output_dir = Path(output_dir)
        self.skip_validation = skip_validation
        self.message_queue = message_queue
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chat_db_path = self._get_chat_db_path()
        self.skipped_files: Dict[str, Dict] = {}
        
    def _log(self, message, level='info'):
        """Log message to both GUI and file."""
        if self.message_queue:
            self.message_queue.put({'type': 'log', 'text': message})
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
        elif level == 'error':
            logger.error(message)

    def _update_progress(self, message, percent=None):
        """Update progress in GUI."""
        if self.message_queue:
            self.message_queue.put({
                'type': 'progress',
                'text': message,
                'percent': percent if percent is not None else 0
            })

    def _get_chat_db_path(self) -> Path:
        """Get the path to the iMessage chat database."""
        home = Path.home()
        # Try both possible locations for the chat.db file
        possible_paths = [
            home / "Library/Messages/chat.db",
            home / "Library/Messages/Archive/chat.db",
            home / "Library/Containers/com.apple.iChat/Data/Library/Messages/chat.db"
        ]
        
        for path in possible_paths:
            if path.exists():
                self._log(f"Found chat database at: {path}")
                return path
                
        raise FileNotFoundError("iMessage database not found. Please ensure Messages is properly set up and synced.")

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize the filename to be safe for all filesystems."""
        # Split filename and extension
        name, ext = os.path.splitext(filename)
        # Remove any path separators and null bytes
        name = re.sub(r'[/\\\\:\*\?"<>\|\x00]', '_', name)
        # Remove any leading/trailing spaces and dots
        name = name.strip('. ')
        # Ensure filename isn't empty
        if not name:
            name = 'unnamed_pdf'
        return f"{name}{ext}"

    def _is_valid_pdf(self, file_path: Path) -> bool:
        """Basic validation that file appears to be a PDF."""
        if self.skip_validation:
            return True
            
        try:
            if not file_path.exists() or not file_path.is_file():
                return False
            
            # Check file size (must be between 100 bytes and 2GB)
            size = file_path.stat().st_size
            if size < 100 or size > 2_000_000_000:
                return False
            
            # Check PDF magic number
            with open(file_path, 'rb') as f:
                header = f.read(4)
                return header.startswith(b'%PDF')
                
        except Exception as e:
            self._log(f"Error validating PDF {file_path}: {e}", level='warning')
            return False

    def _get_attachment_path(self, attachment_id: str) -> Optional[Path]:
        """Get the full path of an attachment from its ID."""
        home = Path.home()
        # Try both possible locations for attachments
        base_paths = [
            home / "Library/Messages/Attachments",
            home / "Library/Containers/com.apple.iChat/Data/Library/Messages/Attachments"
        ]
        
        for base_path in base_paths:
            if not base_path.exists():
                continue
                
            try:
                # Search for the attachment using its ID
                for root, _, files in os.walk(base_path):
                    root_path = Path(root)
                    if attachment_id in root_path.name:
                        # Found the directory containing the attachment
                        pdf_files = list(root_path.glob("*.pdf"))
                        if pdf_files:
                            self._log(f"Found PDF at: {pdf_files[0]}")
                            return pdf_files[0]
            except Exception as e:
                self._log(f"Error searching in {base_path}: {e}", level='warning')
                continue
        
        self._log(f"Could not find attachment with ID: {attachment_id}", level='warning')
        return None

    def _save_summary(self):
        """Save a detailed summary of the extraction process."""
        summary_file = self.output_dir / "extraction_summary.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_pdfs_found": self.total_found,
                "successfully_copied": self.successful_copies,
                "skipped_files": self.skipped_files
            }, f, indent=2)
        
        # Also create a human-readable summary
        readable_summary = self.output_dir / "extraction_summary.txt"
        with open(readable_summary, 'w') as f:
            f.write(f"PDF Extraction Summary\n")
            f.write(f"===================\n\n")
            f.write(f"Timestamp: {datetime.now()}\n")
            f.write(f"Total PDFs found: {self.total_found}\n")
            f.write(f"Successfully copied: {self.successful_copies}\n")
            f.write(f"Skipped files: {len(self.skipped_files)}\n\n")
            
            if self.skipped_files:
                f.write("Skipped Files Details:\n")
                f.write("=====================\n\n")
                for filename, details in self.skipped_files.items():
                    f.write(f"File: {filename}\n")
                    f.write(f"Reason: {details['reason']}\n")
                    f.write(f"Timestamp: {details['timestamp']}\n")
                    if 'error' in details:
                        f.write(f"Error: {details['error']}\n")
                    f.write("\n")

    def extract_pdfs(self, stop_callback=None):
        """Extract PDFs from iMessage attachments."""
        try:
            conn = sqlite3.connect(self.chat_db_path)
            cursor = conn.cursor()
            
            # Get total number of PDFs
            cursor.execute("""
                SELECT COUNT(*) FROM attachment 
                WHERE mime_type = 'application/pdf'
            """)
            total_pdfs = cursor.fetchone()[0]
            self._log(f"Found {total_pdfs} PDFs to extract")
            
            # Query for PDF attachments
            cursor.execute("""
                SELECT ROWID, filename 
                FROM attachment 
                WHERE mime_type = 'application/pdf'
            """)
            
            processed = 0
            for attachment_id, filename in cursor.fetchall():
                if stop_callback and stop_callback():
                    self._log("Extraction stopped by user")
                    break
                    
                processed += 1
                percent = int((processed / total_pdfs) * 100)
                
                try:
                    source_path = self._get_attachment_path(str(attachment_id))
                    if not source_path:
                        self._log(f"Could not find attachment {attachment_id}", level='warning')
                        continue

                    # Sanitize filename and create destination path
                    safe_filename = self._sanitize_filename(filename or f"pdf_{attachment_id}.pdf")
                    dest_path = self.output_dir / safe_filename

                    # Skip if file exists
                    if dest_path.exists():
                        self._log(f"Skipping {safe_filename} - already exists")
                        continue

                    # Copy the file
                    shutil.copy2(source_path, dest_path)
                    
                    # Validate PDF if needed
                    if not self.skip_validation and not self._is_valid_pdf(dest_path):
                        self._log(f"Invalid PDF: {safe_filename}", level='warning')
                        self.skipped_files[str(dest_path)] = {
                            'reason': 'invalid_pdf',
                            'original_name': filename,
                            'attachment_id': attachment_id
                        }
                        dest_path.unlink()  # Remove invalid file
                        continue

                    self._update_progress(
                        f"Extracted {processed}/{total_pdfs}: {safe_filename}",
                        percent=percent
                    )

                except Exception as e:
                    self._log(f"Error processing {filename}: {str(e)}", level='error')
                    continue

            self._save_summary()
            self._log("Extraction complete!")
            
        except Exception as e:
            self._log(f"Error during extraction: {str(e)}", level='error')
            raise
        finally:
            if 'conn' in locals():
                conn.close() 

    def get_pdf_list(self) -> List[Dict[str, Any]]:
        """Get a list of all PDFs in the Messages database."""
        try:
            conn = sqlite3.connect(self.chat_db_path)
            cursor = conn.cursor()
            
            # Query for PDF attachments with message info
            cursor.execute("""
                SELECT 
                    attachment.ROWID as attachment_id,
                    attachment.filename,
                    attachment.total_bytes,
                    message.date,
                    handle.id as sender
                FROM attachment
                JOIN message_attachment_join ON attachment.ROWID = message_attachment_join.attachment_id
                JOIN message ON message.ROWID = message_attachment_join.message_id
                LEFT JOIN handle ON message.handle_id = handle.ROWID
                WHERE attachment.mime_type = 'application/pdf'
                ORDER BY message.date DESC
            """)
            
            pdfs = []
            for row in cursor.fetchall():
                attachment_id, filename, size, date, sender = row
                
                # Convert date from nanoseconds to datetime
                date = datetime.fromtimestamp(date/1e9)
                
                # Get attachment path
                path = self._get_attachment_path(str(attachment_id))
                
                pdfs.append({
                    'id': attachment_id,
                    'filename': filename or f"pdf_{attachment_id}.pdf",
                    'size': size,
                    'date': date.isoformat(),
                    'sender': sender,
                    'path': str(path) if path else None,
                    'exists': path is not None and path.exists()
                })
            
            return pdfs
            
        except Exception as e:
            self._log(f"Error analyzing PDFs: {str(e)}", level='error')
            raise
        finally:
            if 'conn' in locals():
                conn.close() 
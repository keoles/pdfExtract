#!/usr/bin/env python3
import os
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path
import logging
import re
from typing import List, Optional, Dict
import argparse
import json

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class IMessagePDFExtractor:
    def __init__(self, output_dir: str = "extracted_pdfs", dry_run: bool = False, skip_validation: bool = False):
        self.output_dir = Path(output_dir)
        self.dry_run = dry_run
        self.skip_validation = skip_validation
        if not self.dry_run:
            self.output_dir.mkdir(parents=True, exist_ok=True)
        self.chat_db_path = self._get_chat_db_path()
        # Track skipped files and reasons
        self.skipped_files: Dict[str, Dict] = {}
        
    def _get_chat_db_path(self) -> Path:
        """Get the path to the iMessage chat database."""
        home = Path.home()
        chat_db = home / "Library/Messages/chat.db"
        if not chat_db.exists():
            raise FileNotFoundError("iMessage database not found. Make sure you have access to Messages.")
        return chat_db

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
            logger.warning(f"Error validating PDF {file_path}: {e}")
            return False

    def _get_attachment_path(self, attachment_id: str) -> Optional[Path]:
        """Get the full path of an attachment from its ID."""
        home = Path.home()
        base_path = home / "Library/Messages/Attachments"
        
        try:
            # More efficient search using glob
            pattern = f"**/*{attachment_id}*"
            matches = list(base_path.glob(pattern))
            return matches[0] if matches else None
        except Exception as e:
            logger.warning(f"Error finding attachment {attachment_id}: {e}")
            return None

    def _save_summary(self):
        """Save a detailed summary of the extraction process."""
        if not self.dry_run:
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

    def extract_pdfs(self):
        """Extract all PDFs from iMessage database."""
        try:
            # Create a connection to the chat database
            conn = sqlite3.connect(self.chat_db_path)
            cursor = conn.cursor()
            
            # Query to get all PDF attachments
            query = """
            SELECT 
                message.ROWID,
                message.date,
                attachment.filename,
                attachment.ROWID as attachment_id
            FROM message
            JOIN message_attachment_join ON message.ROWID = message_attachment_join.message_id
            JOIN attachment ON message_attachment_join.attachment_id = attachment.ROWID
            WHERE attachment.filename LIKE '%.pdf'
            ORDER BY message.date DESC
            """
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            self.total_found = len(results)
            logger.info(f"Found {self.total_found} PDF attachments")
            if self.dry_run:
                logger.info("DRY RUN: No files will be copied")
            
            self.successful_copies = 0
            for row in results:
                message_id, date, filename, attachment_id = row
                attachment_path = self._get_attachment_path(str(attachment_id))
                
                if not attachment_path or not attachment_path.exists():
                    self.skipped_files[filename] = {
                        "reason": "File not found",
                        "timestamp": datetime.fromtimestamp(date/1e9).isoformat(),
                        "attachment_id": str(attachment_id)
                    }
                    logger.warning(f"Could not find attachment: {filename}")
                    continue
                
                # Validate the PDF
                if not self._is_valid_pdf(attachment_path):
                    self.skipped_files[filename] = {
                        "reason": "Invalid PDF",
                        "timestamp": datetime.fromtimestamp(date/1e9).isoformat(),
                        "path": str(attachment_path)
                    }
                    logger.warning(f"Skipping invalid PDF: {filename}")
                    continue
                    
                # Create a unique filename using original name and timestamp
                timestamp = datetime.fromtimestamp(date/1e9).strftime('%Y%m%d_%H%M%S')
                safe_filename = self._sanitize_filename(filename)
                name, ext = os.path.splitext(safe_filename)
                new_filename = f"{name}_{timestamp}{ext}"
                target_path = self.output_dir / new_filename
                
                # Copy the file to the output directory
                if not self.dry_run:
                    try:
                        shutil.copy2(attachment_path, target_path)
                        self.successful_copies += 1
                        logger.info(f"Copied: {filename}")
                    except Exception as e:
                        self.skipped_files[filename] = {
                            "reason": "Copy failed",
                            "timestamp": datetime.fromtimestamp(date/1e9).isoformat(),
                            "error": str(e),
                            "source": str(attachment_path),
                            "target": str(target_path)
                        }
                        logger.error(f"Failed to copy {filename}: {e}")
                else:
                    logger.info(f"Would copy: {filename}")
            
            conn.close()
            
            # Save the summary
            if not self.dry_run:
                self._save_summary()
            
            if self.dry_run:
                logger.info(f"DRY RUN complete. Would have copied {len(results)} PDFs to: {self.output_dir}")
            else:
                logger.info(f"PDF extraction complete. Successfully copied {self.successful_copies} of {self.total_found} PDFs to: {self.output_dir}")
                logger.info(f"Detailed summary saved to {self.output_dir}/extraction_summary.txt")
            
        except sqlite3.Error as e:
            logger.error(f"Database error: {e}")
            raise
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            raise

def main():
    parser = argparse.ArgumentParser(description='Extract PDFs from iMessage history')
    parser.add_argument('--output-dir', default='extracted_pdfs', help='Directory to save PDFs to')
    parser.add_argument('--skip-validation', action='store_true', help='Skip PDF validation (faster but less safe)')
    parser.add_argument('--no-dry-run', action='store_true', help='Skip dry run and copy files immediately')
    args = parser.parse_args()

    try:
        if not args.no_dry_run:
            # First do a dry run to show what would happen
            logger.info("Performing dry run first...")
            extractor = IMessagePDFExtractor(output_dir=args.output_dir, dry_run=True, skip_validation=args.skip_validation)
            extractor.extract_pdfs()
            
            # Ask for confirmation before proceeding
            response = input("\nWould you like to proceed with copying the files? (yes/no): ").lower().strip()
            if response != 'yes':
                logger.info("Operation cancelled by user")
                return 0
        
        # Proceed with actual extraction
        logger.info("\nProceeding with file extraction...")
        extractor = IMessagePDFExtractor(output_dir=args.output_dir, dry_run=False, skip_validation=args.skip_validation)
        extractor.extract_pdfs()
        return 0
    except Exception as e:
        logger.error(f"Failed to extract PDFs: {e}")
        return 1

if __name__ == "__main__":
    exit(main())

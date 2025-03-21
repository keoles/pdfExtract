# Art Data Extract

A sleek, modern application for syncing iMessages and extracting PDF attachments.

![Screenshot](screenshot.png)

## Features

- Dark-themed modern UI
- Sync iMessages with iCloud
- Extract PDF attachments from iMessage conversations
- Save extracted PDFs to chosen location
- User-friendly interface with clear workflow

## What This App Does

Art Data Extract is designed to help you:

1. **Sync your iMessages** between your Apple devices via iCloud
2. **Extract PDF attachments** that have been sent or received in your iMessage conversations
3. **Organize and save** these PDFs to a location of your choice

This is especially useful for artists, designers, and students who frequently receive PDF documents through iMessage and want an easy way to extract and organize them.

## Installation

### Option 1: Download the Standalone macOS Application (Recommended)

1. [Download the latest release](https://github.com/keoles/pdfExtract/releases) (Art_Data_Extract.dmg)
2. Open the DMG file
3. Drag the "Art Data Extract" application to your Applications folder
4. Launch the application from your Applications folder

When you first run the application, macOS may show a security warning. To allow the app to run:
1. Go to System Preferences > Security & Privacy
2. Click "Open Anyway" to allow the application to run

### Option 2: Clone and Run from Source

```bash
# Clone the repository
git clone https://github.com/keoles/pdfExtract.git

# Navigate to the directory
cd pdfExtract

# Run the installer script
chmod +x install.command
./install.command

# Or run the app directly
chmod +x run.command
./run.command
```

## Usage

### Syncing iMessages

1. Launch Art Data Extract
2. The app will guide you through enabling iMessage sync with iCloud
3. Follow the on-screen instructions to open Messages preferences and enable sync
4. Confirm when sync is complete

### Extracting PDFs

1. After syncing, click "Go to PDF Extractor"
2. Alternatively, run the PDF extractor directly with `./launch_pdf_extractor.command`
3. The app will analyze your messages for PDF attachments
4. Select the PDFs you want to extract
5. Choose an output directory
6. Click "Extract Selected PDFs"

## Building From Source

### Building a Standalone macOS Application

You can build your own standalone application using:

```bash
# Install py2app
pip install py2app

# Build the application
python setup.py py2app

# Create a DMG for distribution
hdiutil create -volname "Art Data Extract" -srcfolder dist/Art\ Data\ Extract.app -ov -format UDZO Art_Data_Extract.dmg
```

## Requirements

- macOS 10.14 or higher
- Python 3.7 or higher
- Messages app configured with iCloud

## Permissions

This app requires:
- Full Disk Access (to read the Messages database)
- Access to your Messages data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Icon created using Python Pillow library
- PDF extraction powered by custom Python code

## Project Structure

- `messages_sync_app.py` - Main application file
- `imessage_pdf_extract.py` - Core functionality for extraction
- `imessage_pdf_extract_gui.py` - GUI implementation
- `pdf_extractor.py` - PDF handling functions
- `setup.py` - Build configuration for standalone app
- `requirements.txt` - Python dependencies
- `run.command` - macOS launch script
- `install.command` - Installation script

## Troubleshooting

### Common Issues

- **App doesn't open**: Make sure Python 3.8+ is installed and in your PATH
- **Message sync doesn't start**: Check if Messages app is properly configured with iMessage
- **Permission errors**: Ensure you've granted necessary permissions to the app

### Logs

Logs are stored in `~/.pdf_rescue_squad/pdf_rescue.log` and can be helpful for troubleshooting.

## Development

### Project Structure

- `messages_sync_app.py` - Main application for syncing iMessages
- `imessage_pdf_extract_gui.py` - PDF extraction interface
- `pdf_extractor.py` - Core PDF extraction functionality

### Building From Source

```bash
# Clone the repository
git clone https://github.com/keoles/pdfExtract.git
cd pdfExtract

# Install development dependencies
pip install -r requirements.txt

# Run tests
python -m unittest discover
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Application uses the [Nord color palette](https://www.nordtheme.com/) for its dark theme
- Inspired by the Equilux GTK theme

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 
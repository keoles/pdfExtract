# Art Data Extract

A sleek, modern dark-themed desktop application for syncing iMessages and extracting PDF attachments on macOS.

![App Screenshot](screenshot.png)

## Features

- Modern, eye-friendly dark UI designed to reduce eye strain
- Guided step-by-step process for syncing iMessages
- Automated tool for extracting PDF attachments from iMessage conversations
- Visual progress indicators
- Minimal and intuitive interface

## Requirements

- macOS (tested on macOS 12 Monterey and newer)
- Python 3.8 or newer
- Messages app with iMessage enabled and configured

## Installation

### Option 1: Using the Installer

1. Download the latest release from the [Releases](https://github.com/yourusername/art-data-extract/releases) page
2. Run the installer: `./install.command`
3. Follow the on-screen instructions

### Option 2: Manual Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/art-data-extract.git
   cd art-data-extract
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python messages_sync_app.py
   ```

## Usage

1. **Start the App**: Launch the application using the `run.command` script or by running `python messages_sync_app.py`

2. **Sync iMessages**:
   - Click the "1: OPEN SETTINGS" button to open Messages preferences
   - Select the "iMessage" tab
   - Click the "Sync Now" button in the Messages preferences
   - Wait for the sync process to complete
   - Return to the Art Data Extract app and click "2: CONFIRM SYNC"

3. **Extract PDFs**:
   - Once sync is confirmed, the "3: EXTRACT MY PDFs" button will be enabled
   - Click it to launch the PDF extraction process
   - Select the output folder for extracted PDFs
   - Follow any additional prompts for extraction options

## Permissions

This application requires:
- Full Disk Access (to read the Messages database)
- Accessibility permissions (to control the Messages app)

You'll be prompted to grant these permissions when running the app for the first time.

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
git clone https://github.com/yourusername/art-data-extract.git
cd art-data-extract

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
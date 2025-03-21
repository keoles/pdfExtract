# Art Data Extract - Usage Guide

This guide provides detailed instructions for using Art Data Extract to sync your iMessages and extract PDF attachments.

## Getting Started

### Installation

1. **Download and Install**:
   - Open the `Art_Data_Extract.dmg` file
   - Drag the application to your Applications folder
   - If prompted about security settings, go to System Preferences > Security & Privacy and click "Open Anyway"

2. **Running from Source** (alternative):
   - Run `./run.command` to start the main application
   - Run `./launch_pdf_extractor.command` to directly open the PDF extractor

### Required Permissions

Art Data Extract needs access to your Messages database to function properly. When first running the app, you may be prompted to:

1. **Grant Full Disk Access**:
   - This is necessary to read the Messages database
   - Go to System Preferences > Security & Privacy > Privacy > Full Disk Access
   - Add the Art Data Extract application to the list of allowed apps

2. **Allow Controlling Messages**:
   - If the app needs to interact with Messages, you'll be prompted to grant permission
   - Follow the on-screen instructions to enable this in System Preferences

## iMessage Sync Process

The app helps you sync your iMessages between your Apple devices using iCloud.

1. **Launch Art Data Extract**
   - Start the app from your Applications folder or using `run.command`

2. **Enable iCloud Sync**
   - The app will guide you through enabling iMessage sync with iCloud
   - You'll need to open Messages preferences and enable Messages in iCloud
   - Follow the on-screen instructions

3. **Wait for Sync Completion**
   - iCloud sync may take time depending on your message volume
   - The app will show a progress indicator
   - Once complete, you'll be able to proceed to PDF extraction

## PDF Extraction

After syncing, you can extract PDF attachments from your iMessage conversations.

1. **Access the PDF Extractor**
   - Click "Go to PDF Extractor" after syncing
   - Or run `./launch_pdf_extractor.command` directly

2. **Select PDFs to Extract**
   - The app will show a list of PDF attachments found in your messages
   - Select the ones you want to extract
   - You can filter by date, contact, or search for specific PDFs

3. **Choose Output Directory**
   - Click "Choose Output Directory" to select where to save extracted PDFs
   - By default, PDFs will be saved to the "extracted_pdfs" folder

4. **Extract the PDFs**
   - Click "Extract Selected PDFs"
   - Wait for the extraction to complete
   - The app will show a success message when finished

5. **View Extracted PDFs**
   - Click "Open Output Folder" to see your extracted PDFs
   - The app preserves original filenames when possible

## Troubleshooting

### Common Issues

1. **App Won't Launch**
   - Make sure Python 3.7+ is installed
   - Run `./run.command` from Terminal to see error messages

2. **Can't Access Messages Database**
   - Grant Full Disk Access as described above
   - Make sure Messages is properly configured with your Apple ID

3. **PDFs Not Found**
   - Make sure iCloud sync has completed
   - Check if your Messages app is properly set up with iCloud

4. **Extraction Errors**
   - Check if you have write permissions to the output directory
   - Ensure enough disk space is available

### Log Files

- App logs are stored in `~/.pdf_rescue_squad/pdf_rescue.log`
- Error logs in the application directory can provide additional information

## Maintenance

To keep the application running smoothly:

1. **Clean Up Temporary Files**
   - Run `./cleanup.command` to remove cache files and build artifacts

2. **Update the Application**
   - Check regularly for updates
   - Download the latest version from the GitHub release page

3. **Rebuild if Needed**
   - If you've modified the source code, rebuild using:
     ```
     ./install.command
     ```

## Getting Help

If you encounter any issues not covered in this guide, please:
1. Check the README.md file for additional information
2. Submit an issue on the GitHub repository
3. Contact the developer directly for support 
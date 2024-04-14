
# SFTP Tool

This script provides functionality to interact with a remote SFTP server, enabling file download, upload, and error handling for file transfers. It uses the paramiko library for SFTP operations and smtplib for sending email notifications.

## Requirements

- Python 3.x
- paramiko library (pip install paramiko)
- dotenv library (pip install python-dotenv)

## Setup

1. Clone the Repository:
    ```bash
    git clone https://github.com/your/repository.git
    cd repository
    ```

2. Install Dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Set Environment Variables:
   Create a `.env` file in the project directory and add the following variables:
    ```plaintext
    SENDER_EMAIL=your_email@gmail.com
    RECEIVER_EMAIL=recipient_email@gmail.com
    KEY=your_email_password_or_app_password
    LOCAL_ERROR_PATH=local/error/
    REMOTE_DOWNLOAD_PATH=/path/to/remote/download/
    LOCAL_DOWNLOAD_PATH=downloads/
    LOCAL_UPLOAD_PATH=export/
    REMOTE_UPLOAD_PATH=/path/to/remote/upload/
    ```

## Usage

Run the script with the required arguments to interact with the SFTP server:
```bash
python sftp_tool.py --hostname <hostname> --username <username> --private-key <path_to_private_key>

## Functionality

- **Download Files from SFTP Server**
  
  Downloads files from the remote SFTP server to the local directory specified in `LOCAL_DOWNLOAD_PATH`.

- **Upload Files to SFTP Server**
  
  Uploads files from the local directory specified in `LOCAL_UPLOAD_PATH` to the remote SFTP server. Handles file aging and error conditions during upload, moving files to the error folder (`LOCAL_ERROR_PATH`) if necessary.

- **Monitor and Handle Error Files**
  
  Monitors the error folder (`LOCAL_ERROR_PATH`) for files that have exceeded an aging threshold (`alert_threshold_seconds`). Moves old files to the error folder on the SFTP server and sends email alerts for error files.

## Command-line Arguments

- `--hostname`: Hostname of the SFTP server (required).
- `--port`: Port number of the SFTP server (default: 22).
- `--username`: Username for SFTP authentication (required).
- `--private-key`: Path to the private key file for SFTP authentication (required).

## Additional Notes

- Ensure that the necessary permissions and access credentials are configured for the SFTP server and SMTP server.
- Customize the email content and error handling logic as per specific requirements.
- Use caution when handling sensitive information like passwords and private keys.

Please refer to the script for detailed implementation and customization options.

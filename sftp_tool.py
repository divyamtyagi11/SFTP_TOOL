import os
import time
import argparse
import paramiko
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
send_flag = False


def send_alert_to_irish_taylor(filename):
    sender_email = os.getenv("SENDER_EMAIL")
    receiver_email = os.getenv("RECEIVER_EMAIL")
    password = os.getenv("KEY")

    # Create EmailMessage object
    message = EmailMessage()
    message["Subject"] = f"File Alert: {filename}"
    message["From"] = sender_email
    message["To"] = receiver_email

    # Compose the email content
    email_content = f"The file '{filename}' has been in the export folder for more than 5 minutes."
    message.set_content(email_content)

    try:
        # Connect to the SMTP server (Outlook SMTP server: smtp-mail.outlook.com, port: 587)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, password)

        # Send the email
        server.send_message(message)

        # Close the connection
        server.quit()
        print("Email notification sent successfully!")

    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")

def establish_sftp_connection(hostname, port, username, private_key_path):
    transport = paramiko.Transport((hostname, port))
    private_key = paramiko.RSAKey.from_private_key_file(private_key_path)
    transport.connect(username=username, pkey=private_key)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp

def download_files_from_sftp(remote_path, local_path, sftp):
    try:
        remote_files = sftp.listdir(remote_path)
        for remote_file in remote_files:
            remote_file_path = os.path.join(remote_path, remote_file)
            local_file_path = os.path.join(local_path, remote_file)
            sftp.get(remote_file_path, local_file_path)
            print(f"Downloaded: {remote_file}")

    except Exception as e:
        print(f"Error downloading files: {str(e)}")

def upload_files_to_sftp(local_path, remote_path, sftp, local_error_path):
    global send_flag
    try:
        local_files = os.listdir(local_path)
        current_time = time.time()
        
        
        for local_file in local_files:
            local_file_path = os.path.join(local_path, local_file)
            remote_file_path = os.path.join(remote_path, local_file)
            
            try:
                # Check if the file is more than 5 minutes old
                file_modified_time = os.path.getmtime(local_file_path)
                if (current_time - file_modified_time) > 300:
                    send_flag = True
                    # Move the old file to the error folder
                    error_folder_path = os.path.join(local_error_path)
                    if not os.path.exists(error_folder_path):
                        os.makedirs(error_folder_path)

                    os.rename(local_file_path, os.path.join(error_folder_path, local_file))
                    print(f"Moved to error folder due to age: {local_file}")
                    continue  # Skip uploading this file
                
                
                sftp.put(local_file_path, remote_file_path)
                print(f"Uploaded: {local_file}")
                
                # If upload is successful, remove the local file
                os.remove(local_file_path)
                print(f"Deleted: {local_file}")
                
            except Exception as upload_error:
                print(f"Error uploading file {local_file}: {str(upload_error)}")
                
                # Move the error file to the error folder
                error_folder_path = os.path.join(local_error_path)
                if not os.path.exists(error_folder_path):
                    os.makedirs(error_folder_path)
                
                os.rename(local_file_path, os.path.join(error_folder_path, local_file))
                print(f"Moved to error folder: {local_file}")

    except Exception as e:
        print(f"Error processing files for upload: {str(e)}")


def monitor_and_alert_error_files(local_error_path, alert_threshold_seconds=300):
    global send_flag
    print("send_flag", send_flag)

    try:
        error_files = [f for f in os.listdir(local_error_path) if os.path.isfile(os.path.join(local_error_path, f))]
        current_time = time.time()
        print(error_files)

        for error_file in error_files:
            print(error_file)
            error_file_path = os.path.join(local_error_path, error_file)
            file_modified_time = os.path.getmtime(error_file_path)

            # Check if the file is older than the alert threshold
            if send_flag:
                print(f"ALERT: Old file detected - {error_file}")

                # Move the old file to the error folder
                error_folder_path = os.path.join(local_error_path)
                if not os.path.exists(error_folder_path):
                    os.makedirs(error_folder_path)

                os.rename(error_file_path, os.path.join(error_folder_path, error_file))
                print(f"Moved to error folder: {error_file}")

                # Send alert email for this error file
                send_alert_to_irish_taylor(error_file)
                send_flag = False

    except Exception as e:
        print(f"Error handling error files: {str(e)}")

def parse_arguments():
    parser = argparse.ArgumentParser(description="SFTP Tool")
    parser.add_argument("--hostname", required=True, help="Hostname of the SFTP server")
    parser.add_argument("--port", type=int, default=22, help="Port number of the SFTP server")
    parser.add_argument("--username", required=True, help="Username for SFTP authentication")
    parser.add_argument("--private-key", required=True, help="Path to private key file for SFTP authentication")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()

    # Establish SFTP connection
    sftp = establish_sftp_connection(args.hostname, args.port, args.username, args.private_key)

    try:
        local_error_path = os.getenv("LOCAL_ERROR_PATH")
        # Function 1: Download files from remote SFTP server
        remote_download_path = os.getenv("REMOTE_DOWNLOAD_PATH")
        local_download_path = os.getenv("LOCAL_DOWNLOAD_PATH")
        download_files_from_sftp(remote_download_path, local_download_path, sftp)

        # Function 2: Upload files to remote SFTP server
        local_upload_path = os.getenv('LOCAL_UPLOAD_PATH')
        remote_upload_path = os.getenv('REMOTE_UPLOAD_PATH')
        upload_files_to_sftp(local_upload_path, remote_upload_path, sftp, local_error_path)

        # Function 3: Monitor and handle error files
        # local_error_path = "local/error/"
        monitor_and_alert_error_files(local_error_path, alert_threshold_seconds=300)

    finally:
        # Close the SFTP connection
        sftp.close()

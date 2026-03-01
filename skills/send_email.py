#!/usr/bin/env python3
import os
import base64
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def load_credentials():
    workspace_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'workspace')
    creds_path = os.path.join(workspace_dir, 'gmail_credentials.json')
    token_path = os.path.join(workspace_dir, 'gmail_token.json')
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(creds_path):
                print(f"Error: Missing {creds_path}.")
                print("Please run `openspider tools email setup` to configure OAuth credentials.")
                return None
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def send_email(to_email, subject, body):
    creds = load_credentials()
    if not creds:
        return False

    try:
        service = build('gmail', 'v1', credentials=creds)
        
        message = MIMEMultipart()
        message['To'] = to_email
        message['Subject'] = subject
        # Create a text/html MIMEText object
        msg = MIMEText(body, 'html')
        message.attach(msg)
        
        # Raw payload needs to be base64url encoded
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        body_payload = {'raw': raw_message}
        
        send_message = service.users().messages().send(userId="me", body=body_payload).execute()
        print(f"Success: Email sent to {to_email}. Message ID: {send_message['id']}")
        return True
        
    except HttpError as error:
        print(f"Error sending email via Gmail API: {error}")
        return False
    except Exception as e:
        print(f"Unexpected error sending email: {str(e)}")
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send an email via Gmail API (OAuth2)")
    parser.add_argument("--setup", action="store_true", help="Perform initial OAuth browser setup")
    parser.add_argument("--to", help="Recipient email address")
    parser.add_argument("--subject", help="Email subject line")
    parser.add_argument("--body", help="Email HTML or Text body")
    
    args = parser.parse_args()
    
    if args.setup:
        creds = load_credentials()
        if creds and creds.valid:
            print("Successfully authenticated and generated token.json!")
    elif args.to and args.subject and args.body:
        send_email(args.to, args.subject, args.body)
    else:
        print("Error: --to, --subject, and --body are required unless running with --setup")

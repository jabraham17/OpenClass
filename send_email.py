import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import argparse
from pprint import pprint, pformat
import re

# define the scopes that the app can access

SCOPES = ['https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify']
APP_NAME = 'Notify System'
CREDS = 'credentials.json'

def get_creds():
    creds = None
    # check for token
    if os.path.exists('token.pickle'):
        # load token
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # if no token or invalid, create them
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS, SCOPES)
            creds = flow.run_local_server(port=0)
        # we have creds, save them
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds


def send_email(creds, sender, recp, subject, body, attch=None):
    service = build('gmail', 'v1', credentials=creds)
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recp
    msg['Subject'] = subject
    msg.attach(MIMEText(body))
    # if an attachment, add the attach
    if attch:
        pass
    
    raw_msg = {'raw': base64.urlsafe_b64encode(msg.as_bytes()).decode()}
    #raw_msg = {'raw', msg.as_string()}
    #message = service.users().messages().send(userId='me', body={'raw', base64.urlsafe_b64encode(msg.as_string())}).execute()
    message = service.users().messages().send(userId='me', body=raw_msg).execute()

def extract_body(msg):
    # we could try to decode the data, much easier to use the snippet
    return msg['snippet']

def extract_subject(msg):
    # get the message headers
    headers = msg['payload']['headers']
    # this is a list of dicts, we want the one with our subject
    subjects = [h['value'] for h in headers if h.get('name', None) == 'Subject']
    if subjects:
        return subjects[0]
    else:
        return ''


def extract_sender(msg):
    # get the message headers
    headers = msg['payload']['headers']
    # this is a list of dicts, we want the one with our sender
    senders = [h['value'] for h in headers if h.get('name', None) == 'From']
    if senders:
        return senders[0]
    else:
        return ''

# check for new emails
def check_email(creds):
    # build service
    service = build('gmail', 'v1', credentials=creds)

    # get all unread ids
    result = service.users().messages().list(userId='me', labelIds='UNREAD').execute()
    unread_msg_ids = result.get('messages', [])

    # get all unread messages paired with id
    unread_msgs_raw = [(service.users().messages().get(userId='me', id=m['id'], format='full').execute(), m['id']) for m in unread_msg_ids]
    # reformat msgs
    unread_msgs = [((extract_sender(m), extract_subject(m), extract_body(m)), ID) for m, ID in unread_msgs_raw]
    return unread_msgs

def mark_as_read(creds, ids):
    # build service
    service = build('gmail', 'v1', credentials=creds)

    # mark the ids as read
    body = {'ids': ids, 'addLabelIds': [], 'removeLabelIds': ['UNREAD']}
    service.users().messages().batchModify(userId='me', body=body).execute()

def cmd_ln_tool():
    argparser = argparse.ArgumentParser(description='Send a test email')
    argparser.add_argument('sender', nargs='?', type=str, help='Email to send from')
    argparser.add_argument('recp', nargs='?', type=str, help='Email to send to')
    argparser.add_argument('-r', action='store_true', help='Whether to read or send')
    args = argparser.parse_args()

    creds = get_creds()

    if args.r:
        # read
        msgs = check_email(creds)
        if msgs:
            print(*msgs, sep='\n')
            # now mark as read
            ids = [m[1] for m in msgs]
            mark_as_read(creds, ids)
        else:
            print('No new messages')
    else:
        # send
        sender = f'"COURSE TRACKER" <{args.sender}>'
        print(sender)
        recp = args.recp
        subject = 'Test Email'
        body = "This is a test email"
        send_email(creds, sender, recp, subject, body)


if __name__ == '__main__':
    cmd_ln_tool()

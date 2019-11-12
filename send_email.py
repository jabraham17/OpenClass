import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# define the scopes that the app can access

SCOPES = ['https://www.googleapis.com/auth/gmail.send','https://www.googleapis.com/auth/gmail.readonly']
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

# check for new emails
def check_email(creds):
    service = build('gmail', 'v1', credentials=creds)
    return []


def cmd_ln_tool():
    argparser = argparse.ArgumentParser(description='Send a test email')
    argparser.add_argument('sender', type=str, help='Email to send from')
    argparser.add_argument('recp', type=str, help='Email to send to')
    args = argparser.parse_args()

    creds = get_creds()
	sender = args.sender
	recp = args.recp
	subject = 'Test Email'
	body = "This is a test email"
	send_email(creds, sender, recp, subject, body)


if __name__ == '__main__':
	cmd_ln_tool()

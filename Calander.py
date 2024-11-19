import re
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import PyPDF2

# Define regular expression patterns for dates and events
date_pattern = re.compile(r'\b\d{4}\b')
event_pattern = re.compile(r'.*?(?=\d{1,2}[./-]|$)')

# Function to authenticate with Google Calendar API
def authenticate_google_calendar_login():
    SCOPES = ['https://www.googleapis.com/auth/calendar',]
    
    flow = InstalledAppFlow.from_client_secrets_file(
        r"C:\Users\depri\Downloads\client_secret_569555353556-05vbtnhika7jgub0pejuekqfhccrtgcb.apps.googleusercontent.com.json", SCOPES)
    creds = flow.run_local_server(port=0)

    with open('token.json', 'w') as token:
        token.write(creds.to_json())

    return creds

# Function to create event on Google Calendar
def create_event(calendar_service, start_time, end_time, summary):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'GMT-5',
        },
        'end': {
            'dateTime': end_time.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'GMT+8',
        },
    }
    try:
        event = calendar_service.events().insert(calendarId='primary', body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))
    except Exception as e:
        print(f"An error occurred while creating the event: {e}")

# Function to extract dates and events from PDF and add to Google Calendar
def process_pdf(pdf_path, creds):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ''.join(page.extract_text() for page in pdf_reader.pages)
    except Exception as e:
        print(f"An error occurred while reading the PDF: {e}")
        return

    dates = date_pattern.findall(text)
    events = event_pattern.findall(text)

    if not dates or not events:
        print("No dates or events found in the PDF.")
        return

    service = build('calendar', 'v3', credentials=creds)

    for date, event in zip(dates, events):
        try:
            # Assuming event duration is 1 hour
            start_time = datetime.datetime(int(date), 1, 1)
            end_time = start_time + datetime.timedelta(hours=1)
            create_event(service, start_time, end_time, event)
        except Exception as e:
            print(f"An error occurred while processing event: {e}")

# Main function
def main():
    creds = authenticate_google_calendar_login()
    process_pdf(r'C:\Users\depri\Downloads\Clanader PDF file\syllabus.pdf', creds)

if __name__ == "__main__":
    main()

import datetime
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Constants
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
TOKEN_FILE = 'token.json'
CREDENTIALS_FILE = 'credentials.json'
TIMEZONE_OFFSET = 'Z'


def load_credentials():
    """Load or refresh credentials for Google API."""
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    else:
        creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())

    return creds


def get_date_range():
    """Get the start of the month and the end of the current day."""
    now = datetime.datetime.utcnow()
    month_start = datetime.datetime(now.year, now.month, 1, 0, 0).isoformat() + TIMEZONE_OFFSET
    today_end = datetime.datetime(now.year, now.month, now.day, 23, 59).isoformat() + TIMEZONE_OFFSET
    return month_start, today_end


def process_events(events, email):
    """Process and print event details, calculate total work time."""
    worktime = 0
    for event in events:
        print(event['summary'], end=' ')

        if event.get('attendees'):
            user_attendee = next((attendee for attendee in event['attendees'] if attendee['email'] == email), None)
            if user_attendee and user_attendee['responseStatus'] == 'declined':
                print('declined')
                continue

        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        duration_hours = (datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).total_seconds() / 3600
        print(duration_hours)
        worktime += duration_hours

    print(f'# Work time: {worktime}h')


def get_calendar_data():
    """Main function to retrieve and process calendar data."""
    creds = load_credentials()

    try:
        service = build('calendar', 'v3', credentials=creds)
        month_start, today_end = get_date_range()

        events_result = service.events().list(calendarId='primary', timeMin=month_start, timeMax=today_end, singleEvents=True, orderBy='startTime').execute()
        email = events_result.get('summary')
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
        else:
            process_events(events, email)

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    get_calendar_data()

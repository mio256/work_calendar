import datetime
import os
import collections
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
    """Get the start and end of the previous month."""
    now = datetime.datetime.utcnow()
    first_day_this_month = datetime.datetime(now.year, now.month, 1)
    last_day_last_month = first_day_this_month - datetime.timedelta(days=1)
    first_day_last_month = datetime.datetime(last_day_last_month.year, last_day_last_month.month, 1)
    month_start = first_day_last_month.isoformat() + TIMEZONE_OFFSET
    month_end = last_day_last_month.isoformat() + TIMEZONE_OFFSET
    return month_start, month_end


def process_events(events):
    """Process events, group by weeks and sum up durations for appointments with the same name."""
    events_by_week = collections.defaultdict(lambda: collections.defaultdict(float))
    for event in events:
        event_name = event['summary']
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        duration_hours = (datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).total_seconds() / 3600
        event_date = datetime.datetime.fromisoformat(start)
        week_number = event_date.isocalendar()[1]
        events_by_week[week_number][event_name] += duration_hours

    for week, events in events_by_week.items():
        print(f"Week {week}:")
        for event_name, total_hours in events.items():
            print(f"  {event_name}: {total_hours} hours")


def get_calendar_data():
    """Main function to retrieve and process calendar data."""
    creds = load_credentials()

    try:
        service = build('calendar', 'v3', credentials=creds)
        month_start, month_end = get_date_range()

        events_result = service.events().list(calendarId='primary', timeMin=month_start, timeMax=month_end, singleEvents=True, orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No events found for the last month.')
        else:
            process_events(events)

    except HttpError as error:
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    get_calendar_data()

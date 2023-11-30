import datetime
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

LIMIT = 50


def get_nth_week2_datetime_dt(dt, firstweekday=0):
    first_dow = dt.replace(day=1).weekday()
    offset = (first_dow - firstweekday) % 7
    return (dt.day + offset - 1) // 7 + 1


def get_calendar_data():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow()
        month_start = datetime.datetime(now.year, now.month, 1, 0, 0).isoformat() + '+09:00'
        today_end = datetime.datetime(now.year, now.month, now.day, 23, 59).isoformat() + '+09:00'
        # calc days
        days = (datetime.datetime.fromisoformat(today_end) - datetime.datetime.fromisoformat(month_start)).days + 1
        events_result = service.events().list(calendarId='primary',
                                              timeMin=month_start,
                                              timeMax=today_end,
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        email = events_result.get('summary')
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        worktime = 0
        for event in events:
            print(event['summary'], end=' ')
            if event.get('attendees', []):
                user_attendee = next((attendee for attendee in event['attendees'] if attendee['email'] == email), None)
                if user_attendee and user_attendee['responseStatus'] == 'declined':
                    print('declined')
                    continue
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            hours = (datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)).total_seconds() / 3600
            print(hours)
            worktime += hours
        print(f'Work time : {worktime}h')

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    get_calendar_data()

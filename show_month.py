import pprint
import datetime
import os.path
import calendar

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


def main():
    data = get_calendar_data()
    pprint.pprint(data)


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
        events_result = service.events().list(calendarId='primary',
                                              timeMin=datetime.datetime(now.year, now.month, 1, 0, 0).isoformat() + '+09:00',
                                              timeMax=datetime.datetime(now.year, now.month, calendar.monthrange(now.year, now.month)[1], 23, 59).isoformat() + '+09:00',
                                              singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        data = [{}, {}, {}, {}, {}, {}, {}]
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            time = datetime.datetime.fromisoformat(end) - datetime.datetime.fromisoformat(start)
            try:
                data[get_nth_week2_datetime_dt(datetime.datetime.fromisoformat(start))][event['summary']] += time.seconds//60
            except:
                data[get_nth_week2_datetime_dt(datetime.datetime.fromisoformat(start))][event['summary']] = time.seconds//60
        return data

    except HttpError as error:
        print('An error occurred: %s' % error)


if __name__ == '__main__':
    main()

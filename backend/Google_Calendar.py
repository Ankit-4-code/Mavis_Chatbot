import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import os

# Path setup for credentials and token
current_dir = os.path.dirname(os.path.abspath(__file__))
credentials_path = os.path.join(current_dir, '..', 'credentials.json')
token_path = os.path.join(current_dir, '..', 'token.json')
# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def calendar(timeMin = None, timeMax = None):
    ## Prints the start and name of the next 10 events on the user's calendar.

    creds = None
    response_text = ""
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        if timeMin:

            timeMin = datetime.datetime.strptime(timeMin,'%Y-%m-%d').isoformat() + 'Z' ## 'Z' indicates UTC time
        else:
            ## Date will be now(Today)
            timeMin = datetime.datetime.utcnow().isoformat()+ 'Z'
        
        if timeMax :
            ## Add a day to include the events on the endDate
            timeMax = (datetime.datetime.strptime(timeMax, '%Y-%m-%d')).isoformat() + 'Z'

        # Call the Calendar API
    
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=timeMin,timeMax=timeMax,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return('No upcoming events found.')

        # Prints the start and name of the next 10 events
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(start, event['summary'])
            response_text += f"{start} {event['summary']}\n"

    except HttpError as error:
        print('An error occurred: %s' % error)
        response_text = f"An error occured: {error}"

    return response_text



#if __name__ == '__main__' :
    #calendar()

    

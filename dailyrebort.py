import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from collections import defaultdict
from datetime import datetime, timedelta, time
from googleapiclient.discovery import build
import pytz


# the scopes required for accessing Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

# the file token.pickle stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
def authenticate():
  creds = None
  token_path = 'token.pickle'

  if os.path.exists(token_path):
    with open(token_path, 'rb') as token_file:
      creds = pickle.load(token_file)

  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file('./credentials.json', SCOPES)
      creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open(token_path, 'wb') as token_file:
      pickle.dump(creds, token_file)

  return creds


# analyze the events by partial title match 
def analyze_events(events):
  title_blocks = defaultdict(timedelta)
  last_event_end = None

  for event in events:
    start_time = event['start'].get('dateTime', event['start'].get('date'))
    end_time = event['end'].get('dateTime', event['end'].get('date'))
    # fix duration TypeError: unsupported operand type(s) for -: 'str' and 'str'
    duration = (datetime.fromisoformat(end_time) - datetime.fromisoformat(start_time)).total_seconds() / 3600
    
    title = event['summary'].lower()

    
    # Check for uncounted time between events
    if last_event_end:
      uncounted_duration = (datetime.fromisoformat(start_time) - last_event_end).total_seconds() / 3600
      title_blocks['uncounted time'] += timedelta(hours=uncounted_duration)

    # check for common keywords
    if 'eating'in title or 'lunch' in title or 'eat' in title or 'breakfast' in title or 'dinner' in title or 'snack' in title:
      title_blocks['eating'] += timedelta(hours=duration)
    elif 'sleep' in title:
      title_blocks['sleep'] += timedelta(hours=duration)
    elif 'work' in title or 'flawless' in title:
      title_blocks['work'] += timedelta(hours=duration)
    elif 'workout' in title or 'cycle' in title or 'exercise' in title or 'walking' in title or 'running' in title:
      title_blocks['workout'] += timedelta(hours=duration)
    elif 'study' in title or 'class' in title or 'lab' in title or 'assignment' in title or 'collage' in title or 'university' in title or 'exam' in title:
      title_blocks['for university'] += timedelta(hours=duration)
    elif 'meeting' in title:
      title_blocks['meeting'] += timedelta(hours=duration)
    elif 'reading' in title:
      title_blocks['reading'] += timedelta(hours=duration)
    elif 'summary' in title:
      title_blocks['writing book summary'] += timedelta(hours=duration)
    elif 'planning' in title:
      title_blocks['planning'] += timedelta(hours=duration)
    elif 'prayer' in title:
      title_blocks['prayer'] += timedelta(hours=duration)
    elif 'cleaning' in title or 'home keeping' in title or 'wash deshes' in title:
      title_blocks['cleaning'] += timedelta(hours=duration)
    elif 'shopping' in title or 'outside' in title or 'car' in title:
      title_blocks['outhome activity'] += timedelta(hours=duration)
    elif 'gaming' in title or 'game' in title:
      title_blocks['gaming'] += timedelta(hours=duration)
    elif 'movie' in title or 'tv' in title:
      title_blocks['watching'] += timedelta(hours=duration)
    elif 'phone' in title:
      title_blocks['phone'] += timedelta(hours=duration)
    elif 'social' in title or 'friends' in title:
      title_blocks['social life'] += timedelta(hours=duration)
    elif 'bath' in title or 'shower' in title or 'self care' in title:
      title_blocks['self care'] += timedelta(hours=duration)
    elif 'travel' in title or 'trip' in title:
      title_blocks['travel'] += timedelta(hours=duration)
    elif 'hobby' in title or 'painting' in title or 'drawing' in title or 'hobbies' in title:
      title_blocks['hobby'] += timedelta(hours=duration)
    elif 'family' in title or 'mom' in title or 'dad' in title or 'brother' in title or 'sister' in title:
      title_blocks['family'] += timedelta(hours=duration)
    elif 'journaling' in title:
      title_blocks['journaling'] += timedelta(hours=duration)
    elif 'insta post' in title or 'content' in title:
      title_blocks['content creation'] += timedelta(hours=duration)
    elif 'learning' in title or 'course' in title or 'lecture' in title or 'learn' in title:
      title_blocks['learning'] += timedelta(hours=duration)
    elif 'coding' in title or 'code' in title:
      title_blocks['coding'] += timedelta(hours=duration)
    elif 'on bed' in title:
      title_blocks['on bed'] += timedelta(hours=duration)
    elif 'cooking' in title or 'baking' in title:
      title_blocks['cooking'] += timedelta(hours=duration)
    elif 'article' in title:
      title_blocks['article reading'] += timedelta(hours=duration)
    elif 'googling' in title or 'searching' in title or 'sufing' in title:
      title_blocks['googling'] += timedelta(hours=duration)
    elif 'youtube' in title:
      title_blocks['youtube'] += timedelta(hours=duration)
    elif 'novel' in title:
      title_blocks['novel reading'] += timedelta(hours=duration)
    elif 'podcast' in title:
      title_blocks['podcast'] += timedelta(hours=duration)
    elif 'quran' in title:
      title_blocks['quran'] += timedelta(hours=duration)
    elif 'freelance' in title:
      title_blocks['freelance activity'] += timedelta(hours=duration)
    else:
      title_blocks['other'] += timedelta(hours=duration)
    
    last_event_end = datetime.fromisoformat(end_time)
  
  return title_blocks


def main():
  creds = authenticate()
  service = build('calendar', 'v3', credentials=creds)
  
  # Get Riyadh time zone
  riyadh_timezone = pytz.timezone('Asia/Riyadh')
  
  # Get current time in Riyadh
  now = datetime.now(riyadh_timezone)
  # Calculate start and end times for yesterday in Riyadh time zone
  yesterday = now - timedelta(days=1)
  start_time = yesterday.astimezone(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
  end_time = yesterday.astimezone(pytz.utc).replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()
  
  yesterday_events_result = service.events().list(
    calendarId='primary',
    timeMin=start_time,
    timeMax=end_time,
    maxResults=1000,
    singleEvents=True,
    orderBy='startTime'
  ).execute()

  events = yesterday_events_result.get('items', [])
  analyzed_data = analyze_events(events)

  print('\nYesterday\'s events :')

  total_duration = 0
  for title, duration in analyzed_data.items():
    print(f'{title} : {duration}')
    # get duration in hours
    total_duration += duration.total_seconds() / 3600
  print(f'Total duration : {total_duration.__round__(2)} hours')

  # Calculate start and end times for the past week in Riyadh time zone
  past_week = now - timedelta(days=7)
  start_time = past_week.astimezone(pytz.utc).replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
  end_time = now.astimezone(pytz.utc).replace(hour=23, minute=59, second=59, microsecond=999999).isoformat()

  past_week_events_result = service.events().list(
    calendarId='primary',
    timeMin=start_time,
    timeMax=end_time,
    maxResults=1000,
    singleEvents=True,
    orderBy='startTime'
  ).execute()

  pastweek_events = past_week_events_result.get('items', [])
  week_analyzed_data = analyze_events(pastweek_events)

  print('\nLast week data:')

  week_total_duration = 0
  for title, duration in week_analyzed_data.items():
    print(f'{title} : {duration}')
    # get duration in hours
    week_total_duration += duration.total_seconds() / 3600
  print(f'Total duration : {week_total_duration.__round__(2)} hours')


if __name__ == '__main__':
  main()
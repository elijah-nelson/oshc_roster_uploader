import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from functools import cache

# If modifying these scopes, delete the file token.json.
SCOPES = [
    "https://www.googleapis.com/auth/calendar",
    "https://www.googleapis.com/auth/calendar.events",
]

AUTH_FOLDER = "auth"
TOKEN_PATH = os.path.join(AUTH_FOLDER, "token.json")
CREDS_PATH = os.path.join(AUTH_FOLDER, "credentials.json")

ELI_AND_AMY_CALENDAR_ID = "0ni1o3c39sd0r0boommkg87kkg@group.calendar.google.com"

if not os.path.exists(AUTH_FOLDER):
    os.makedirs(AUTH_FOLDER)


@cache
def get_service():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_PATH):
        print("Using existing token", TOKEN_PATH)
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())

    return build("calendar", "v3", credentials=creds)


def get_events(
    timeMin: str | None = None,
    timeMax: str | None = None,
    maxResults: int | None = None,
) -> list[dict]:

    service = get_service()
    events_result: dict = (
        service.events()
        .list(
            calendarId=ELI_AND_AMY_CALENDAR_ID,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=maxResults,  # maximum allowed value is 2500
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    event_objects = events_result.get("items", [])

    events = []
    for event_obj in event_objects:
        start, end = event_obj["start"], event_obj["end"]

        if "dateTime" not in start or "dateTime" not in end:
            continue  # ignore all day events

        events.append(
            {
                "event_name": event_obj["summary"],
                "event_start": start["dateTime"],
                "event_end": end["dateTime"],
            }
        )

    return events


def add_events(events: list[dict[str, str]]):
    """Adds all events that don't currently exist."""
    if not events:
        print("No events to add")
        return

    service = get_service()

    earliest_start = min(event["event_start"] for event in events)
    latest_end = max(event["event_end"] for event in events)

    current_events = get_events(timeMin=earliest_start, timeMax=latest_end)

    new_events = [event for event in events if event not in current_events]

    if not new_events:
        print("No new events to add")
        return

    for event in new_events:
        event_result = (
            service.events()
            .insert(
                calendarId=ELI_AND_AMY_CALENDAR_ID,
                body={
                    "summary": event["event_name"],
                    "start": {
                        "dateTime": event["event_start"],
                    },
                    "end": {
                        "dateTime": event["event_end"],
                    },
                },
            )
            .execute()
        )
        print(f"Event created: {event_result['htmlLink']}")


def main():
    events_to_add = [
        {
            "event_name": "Test event",
            "event_end": "2024-09-28T10:00:00+10:00",
            "event_start": "2024-09-28T09:00:00+10:00",
        }
    ]

    add_events(events_to_add)


if __name__ == "__main__":
    main()

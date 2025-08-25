#!/usr/bin/env python3
"""
Calendar Manager - A high-level abstraction for Google Calendar operations
"""

import os
import pickle
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import pytz
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class EventStatus(Enum):
    ACCEPTED = "accepted"
    DECLINED = "declined"
    TENTATIVE = "tentative"
    NEEDS_ACTION = "needsAction"

class EventColor(Enum):
    BLUE = "9"       # Focus time
    GRAY = "8"       # Commute/buffer
    RED = "11"       # Critical
    GREEN = "10"     # Available
    YELLOW = "5"     # Tentative

@dataclass
class CalendarEvent:
    """Structured representation of a calendar event"""
    id: str
    title: str
    start: datetime
    end: datetime
    status: EventStatus = EventStatus.ACCEPTED
    location: Optional[str] = None
    description: Optional[str] = None
    attendees: List[Dict] = None
    has_meeting_link: bool = False
    
    @property
    def duration_minutes(self) -> int:
        return int((self.end - self.start).total_seconds() / 60)
    
    @property
    def is_focus_block(self) -> bool:
        return "Focus Block" in self.title or "🎯" in self.title
    
    @property
    def is_commute(self) -> bool:
        return "Commute" in self.title or "🚗" in self.title

class CalendarManager:
    """High-level calendar management interface"""
    
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    IST = pytz.timezone('Asia/Kolkata')
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.pickle'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Google Calendar service with authentication"""
        creds = self._get_credentials()
        self.service = build('calendar', 'v3', credentials=creds)
    
    def _get_credentials(self):
        """Handle OAuth2 authentication and token management"""
        creds = None
        
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f'{self.credentials_path} not found. Please set up Google Calendar API credentials.')
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, self.SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def get_today_events(self, include_declined: bool = False) -> List[CalendarEvent]:
        """Fetch all events for today"""
        now = datetime.now(self.IST)
        return self.get_events_for_date(now.date(), include_declined)
    
    def get_events_for_date(self, date, include_declined: bool = False) -> List[CalendarEvent]:
        """Fetch all events for a specific date"""
        start_of_day = datetime.combine(date, datetime.min.time()).replace(tzinfo=self.IST)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self.get_events_in_range(start_of_day, end_of_day, include_declined)
    
    def get_events_in_range(self, start: datetime, end: datetime, include_declined: bool = False) -> List[CalendarEvent]:
        """Fetch events within a time range"""
        events_result = self.service.events().list(
            calendarId='primary',
            timeMin=start.isoformat(),
            timeMax=end.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = []
        for event_data in events_result.get('items', []):
            event = self._parse_event(event_data)
            if include_declined or event.status != EventStatus.DECLINED:
                events.append(event)
        
        return events
    
    def _parse_event(self, event_data: Dict) -> CalendarEvent:
        """Parse Google Calendar event data into CalendarEvent object"""
        # Parse datetime
        start_str = event_data['start'].get('dateTime', event_data['start'].get('date'))
        end_str = event_data['end'].get('dateTime', event_data['end'].get('date'))
        
        if 'T' in start_str:
            start_dt = datetime.fromisoformat(start_str.replace('Z', '+00:00')).astimezone(self.IST)
            end_dt = datetime.fromisoformat(end_str.replace('Z', '+00:00')).astimezone(self.IST)
        else:
            start_dt = datetime.fromisoformat(start_str).replace(tzinfo=self.IST)
            end_dt = datetime.fromisoformat(end_str).replace(tzinfo=self.IST)
        
        # Get my response status
        status = EventStatus.ACCEPTED
        attendees = event_data.get('attendees', [])
        for attendee in attendees:
            if attendee.get('self', False):
                status = EventStatus(attendee.get('responseStatus', 'accepted'))
                break
        
        # Check for meeting links
        has_meeting_link = bool(event_data.get('hangoutLink'))
        if not has_meeting_link and 'description' in event_data:
            desc = event_data['description'].lower()
            has_meeting_link = any(keyword in desc for keyword in ['zoom', 'meet', 'teams'])
        
        return CalendarEvent(
            id=event_data['id'],
            title=event_data.get('summary', 'No Title'),
            start=start_dt,
            end=end_dt,
            status=status,
            location=event_data.get('location'),
            description=event_data.get('description'),
            attendees=attendees,
            has_meeting_link=has_meeting_link
        )
    
    def create_event(self, 
                    title: str,
                    start: datetime,
                    end: datetime,
                    description: str = None,
                    location: str = None,
                    color: EventColor = None,
                    reminder_minutes: int = 5) -> CalendarEvent:
        """Create a new calendar event"""
        event_body = {
            'summary': title,
            'start': {
                'dateTime': start.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'end': {
                'dateTime': end.isoformat(),
                'timeZone': 'Asia/Kolkata',
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': reminder_minutes},
                ],
            },
        }
        
        if description:
            event_body['description'] = description
        if location:
            event_body['location'] = location
        if color:
            event_body['colorId'] = color.value
        
        created_event = self.service.events().insert(calendarId='primary', body=event_body).execute()
        return self._parse_event(created_event)
    
    def create_focus_block(self, 
                          title: str,
                          start: datetime,
                          end: datetime,
                          description: str = None) -> CalendarEvent:
        """Create a focus time block"""
        return self.create_event(
            title=f"🎯 Focus Block: {title}",
            start=start,
            end=end,
            description=description or f"Deep work session on {title}",
            color=EventColor.BLUE,
            reminder_minutes=5
        )
    
    def create_commute_block(self, start: datetime, end: datetime, description: str = "Travel time") -> CalendarEvent:
        """Create a commute/buffer block"""
        return self.create_event(
            title="🚗 Commute",
            start=start,
            end=end,
            description=description,
            color=EventColor.GRAY,
            reminder_minutes=10
        )
    
    def update_event_status(self, event_id: str, new_status: EventStatus, send_notification: bool = True) -> bool:
        """Update your response status for an event"""
        try:
            event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
            
            attendees = event.get('attendees', [])
            for attendee in attendees:
                if attendee.get('self', False):
                    attendee['responseStatus'] = new_status.value
                    break
            
            self.service.events().patch(
                calendarId='primary',
                eventId=event_id,
                body={'attendees': attendees},
                sendUpdates='all' if send_notification else 'none'
            ).execute()
            return True
        except Exception as e:
            print(f"Error updating event status: {e}")
            return False
    
    def decline_event(self, event_id: str, send_notification: bool = True) -> bool:
        """Decline a calendar event"""
        return self.update_event_status(event_id, EventStatus.DECLINED, send_notification)
    
    def reschedule_event(self, 
                        event_id: str,
                        new_start: datetime,
                        new_end: datetime,
                        message: str = None,
                        send_notification: bool = True) -> CalendarEvent:
        """Reschedule an existing event"""
        event = self.service.events().get(calendarId='primary', eventId=event_id).execute()
        
        event['start']['dateTime'] = new_start.isoformat()
        event['end']['dateTime'] = new_end.isoformat()
        
        if message:
            current_desc = event.get('description', '')
            event['description'] = f'Rescheduled: {message}\n\n{current_desc}' if current_desc else f'Rescheduled: {message}'
        
        updated_event = self.service.events().update(
            calendarId='primary',
            eventId=event_id,
            body=event,
            sendUpdates='all' if send_notification else 'none'
        ).execute()
        
        return self._parse_event(updated_event)
    
    def find_event_by_title(self, title_substring: str, date=None) -> Optional[CalendarEvent]:
        """Find an event by partial title match"""
        events = self.get_today_events() if date is None else self.get_events_for_date(date)
        
        for event in events:
            if title_substring.lower() in event.title.lower():
                return event
        return None
    
    def analyze_schedule(self, date=None) -> Dict:
        """Analyze schedule and provide insights"""
        events = self.get_today_events() if date is None else self.get_events_for_date(date)
        
        total_meetings = len([e for e in events if not e.is_focus_block and not e.is_commute])
        total_focus_time = sum([e.duration_minutes for e in events if e.is_focus_block])
        total_meeting_time = sum([e.duration_minutes for e in events if not e.is_focus_block and not e.is_commute])
        
        # Find free blocks
        free_blocks = self._find_free_blocks(events)
        
        return {
            'total_events': len(events),
            'total_meetings': total_meetings,
            'focus_hours': total_focus_time / 60,
            'meeting_hours': total_meeting_time / 60,
            'free_blocks': free_blocks,
            'back_to_back_count': self._count_back_to_back(events)
        }
    
    def _find_free_blocks(self, events: List[CalendarEvent], min_duration_minutes: int = 30) -> List[Tuple[datetime, datetime]]:
        """Find free time blocks in schedule"""
        if not events:
            return []
        
        events = sorted(events, key=lambda e: e.start)
        free_blocks = []
        
        # Check time before first event
        work_start = datetime.now(self.IST).replace(hour=9, minute=0, second=0, microsecond=0)
        if events[0].start > work_start:
            duration = (events[0].start - work_start).total_seconds() / 60
            if duration >= min_duration_minutes:
                free_blocks.append((work_start, events[0].start))
        
        # Check gaps between events
        for i in range(len(events) - 1):
            gap_start = events[i].end
            gap_end = events[i + 1].start
            duration = (gap_end - gap_start).total_seconds() / 60
            if duration >= min_duration_minutes:
                free_blocks.append((gap_start, gap_end))
        
        # Check time after last event
        work_end = datetime.now(self.IST).replace(hour=22, minute=0, second=0, microsecond=0)
        if events[-1].end < work_end:
            duration = (work_end - events[-1].end).total_seconds() / 60
            if duration >= min_duration_minutes:
                free_blocks.append((events[-1].end, work_end))
        
        return free_blocks
    
    def _count_back_to_back(self, events: List[CalendarEvent]) -> int:
        """Count back-to-back meetings (less than 15 min gap)"""
        if len(events) < 2:
            return 0
        
        events = sorted(events, key=lambda e: e.start)
        count = 0
        
        for i in range(len(events) - 1):
            gap = (events[i + 1].start - events[i].end).total_seconds() / 60
            if gap < 15:
                count += 1
        
        return count
    
    def stack_rank_meetings(self, events: List[CalendarEvent] = None) -> Dict[str, List[CalendarEvent]]:
        """Stack rank meetings by importance"""
        if events is None:
            events = self.get_today_events()
        
        # Filter out focus blocks and commute
        meetings = [e for e in events if not e.is_focus_block and not e.is_commute]
        
        critical = []
        important = []
        moderate = []
        cancelable = []
        
        for meeting in meetings:
            title_lower = meeting.title.lower()
            
            # Critical indicators
            if any(word in title_lower for word in ['production', 'deploy', 'leads', 'epd', 'gtm', 'critical', 'urgent']):
                critical.append(meeting)
            # Important indicators
            elif any(word in title_lower for word in ['daily', 'migration', 'customer', 'onboarding', '1:1', 'weekly']):
                important.append(meeting)
            # Generic sync indicators
            elif any(word in title_lower for word in ['sync', 'catch', 'check']):
                moderate.append(meeting)
            # Short meetings or lists
            elif meeting.duration_minutes <= 30 or 'list' in title_lower:
                cancelable.append(meeting)
            else:
                moderate.append(meeting)
        
        return {
            'critical': critical,
            'important': important,
            'moderate': moderate,
            'cancelable': cancelable
        }
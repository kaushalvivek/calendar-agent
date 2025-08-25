#!/usr/bin/env python3
"""
Calendar CLI - Command-line interface for calendar operations
"""

import argparse
from datetime import datetime, timedelta
from calendar_manager import CalendarManager, EventStatus, EventColor

def format_time(dt: datetime) -> str:
    """Format datetime to readable time string"""
    return dt.strftime("%-I:%M %p")

def format_duration(minutes: int) -> str:
    """Format duration in minutes to readable string"""
    hours = minutes // 60
    mins = minutes % 60
    if hours > 0:
        return f"{hours}h {mins}m" if mins > 0 else f"{hours}h"
    return f"{mins}m"

def cmd_today(args):
    """Show today's calendar"""
    manager = CalendarManager()
    events = manager.get_today_events(include_declined=args.all)
    
    if not events:
        print("No events scheduled for today.")
        return
    
    print(f"\n📅 Today's Schedule ({datetime.now().strftime('%A, %B %d, %Y')})")
    print("=" * 60)
    
    for event in events:
        status_icon = {
            EventStatus.ACCEPTED: "✅",
            EventStatus.DECLINED: "❌",
            EventStatus.TENTATIVE: "❓",
            EventStatus.NEEDS_ACTION: "⏳"
        }.get(event.status, "")
        
        time_str = f"{format_time(event.start)} - {format_time(event.end)}"
        duration_str = format_duration(event.duration_minutes)
        
        print(f"\n{status_icon} {time_str} ({duration_str})")
        print(f"   {event.title}")
        if event.location:
            print(f"   📍 {event.location}")
        if event.has_meeting_link:
            print(f"   🔗 Virtual Meeting")

def cmd_analyze(args):
    """Analyze schedule and show insights"""
    manager = CalendarManager()
    analysis = manager.analyze_schedule()
    
    print("\n📊 Schedule Analysis")
    print("=" * 60)
    print(f"Total Events: {analysis['total_events']}")
    print(f"Total Meetings: {analysis['total_meetings']}")
    print(f"Focus Time: {analysis['focus_hours']:.1f} hours")
    print(f"Meeting Time: {analysis['meeting_hours']:.1f} hours")
    print(f"Back-to-back Meetings: {analysis['back_to_back_count']}")
    
    if analysis['free_blocks']:
        print("\n🆓 Available Time Blocks:")
        for start, end in analysis['free_blocks']:
            duration = int((end - start).total_seconds() / 60)
            print(f"   {format_time(start)} - {format_time(end)} ({format_duration(duration)})")

def cmd_rank(args):
    """Stack rank meetings by importance"""
    manager = CalendarManager()
    rankings = manager.stack_rank_meetings()
    
    print("\n📊 Meeting Priority Rankings")
    print("=" * 60)
    
    categories = [
        ("🔴 Critical - Do Not Cancel", rankings['critical']),
        ("🟡 Important - Try to Keep", rankings['important']),
        ("🟢 Moderate - Can Reschedule", rankings['moderate']),
        ("🔵 Cancel Candidates", rankings['cancelable'])
    ]
    
    for category_name, events in categories:
        if events:
            print(f"\n{category_name}:")
            for event in events:
                print(f"   • {format_time(event.start)} - {event.title}")

def cmd_decline(args):
    """Decline a meeting"""
    manager = CalendarManager()
    event = manager.find_event_by_title(args.title)
    
    if not event:
        print(f"❌ Could not find event matching '{args.title}'")
        return
    
    if manager.decline_event(event.id, send_notification=not args.no_notify):
        print(f"✅ Declined: {event.title}")
        print(f"   Time: {format_time(event.start)} - {format_time(event.end)}")
        if not args.no_notify:
            print("   Notification sent to attendees")
    else:
        print(f"❌ Failed to decline event")

def cmd_reschedule(args):
    """Reschedule a meeting"""
    manager = CalendarManager()
    event = manager.find_event_by_title(args.title)
    
    if not event:
        print(f"❌ Could not find event matching '{args.title}'")
        return
    
    # Parse new time
    new_start = event.start + timedelta(minutes=args.shift_minutes)
    new_end = event.end + timedelta(minutes=args.shift_minutes)
    
    updated = manager.reschedule_event(
        event.id, 
        new_start, 
        new_end,
        message=args.message,
        send_notification=not args.no_notify
    )
    
    print(f"✅ Rescheduled: {event.title}")
    print(f"   Old time: {format_time(event.start)} - {format_time(event.end)}")
    print(f"   New time: {format_time(new_start)} - {format_time(new_end)}")
    if args.message:
        print(f"   Message: {args.message}")

def cmd_focus(args):
    """Create a focus block"""
    manager = CalendarManager()
    
    # Parse times
    today = datetime.now().date()
    start_time = datetime.strptime(args.start, "%H:%M").time()
    end_time = datetime.strptime(args.end, "%H:%M").time()
    
    start = datetime.combine(today, start_time).replace(tzinfo=manager.IST)
    end = datetime.combine(today, end_time).replace(tzinfo=manager.IST)
    
    event = manager.create_focus_block(args.title, start, end, args.description)
    
    duration = event.duration_minutes
    print(f"✅ Focus block created: {event.title}")
    print(f"   Time: {format_time(event.start)} - {format_time(event.end)}")
    print(f"   Duration: {format_duration(duration)}")

def cmd_commute(args):
    """Create a commute block"""
    manager = CalendarManager()
    
    # Parse times
    today = datetime.now().date()
    start_time = datetime.strptime(args.start, "%H:%M").time()
    end_time = datetime.strptime(args.end, "%H:%M").time()
    
    start = datetime.combine(today, start_time).replace(tzinfo=manager.IST)
    end = datetime.combine(today, end_time).replace(tzinfo=manager.IST)
    
    event = manager.create_commute_block(start, end, args.description)
    
    print(f"✅ Commute block created")
    print(f"   Time: {format_time(event.start)} - {format_time(event.end)}")

def main():
    parser = argparse.ArgumentParser(description='Calendar Management CLI')
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Today command
    today_parser = subparsers.add_parser('today', help='Show today\'s calendar')
    today_parser.add_argument('--all', action='store_true', help='Include declined events')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze schedule')
    
    # Rank command
    rank_parser = subparsers.add_parser('rank', help='Stack rank meetings by importance')
    
    # Decline command
    decline_parser = subparsers.add_parser('decline', help='Decline a meeting')
    decline_parser.add_argument('title', help='Partial title of meeting to decline')
    decline_parser.add_argument('--no-notify', action='store_true', help='Don\'t send notification')
    
    # Reschedule command
    reschedule_parser = subparsers.add_parser('reschedule', help='Reschedule a meeting')
    reschedule_parser.add_argument('title', help='Partial title of meeting to reschedule')
    reschedule_parser.add_argument('--shift-minutes', type=int, required=True, help='Minutes to shift (positive=later)')
    reschedule_parser.add_argument('--message', help='Message to include with reschedule')
    reschedule_parser.add_argument('--no-notify', action='store_true', help='Don\'t send notification')
    
    # Focus command
    focus_parser = subparsers.add_parser('focus', help='Create focus block')
    focus_parser.add_argument('title', help='Focus block title')
    focus_parser.add_argument('start', help='Start time (HH:MM)')
    focus_parser.add_argument('end', help='End time (HH:MM)')
    focus_parser.add_argument('--description', help='Focus block description')
    
    # Commute command
    commute_parser = subparsers.add_parser('commute', help='Create commute block')
    commute_parser.add_argument('start', help='Start time (HH:MM)')
    commute_parser.add_argument('end', help='End time (HH:MM)')
    commute_parser.add_argument('--description', default='Travel time', help='Commute description')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Execute command
    commands = {
        'today': cmd_today,
        'analyze': cmd_analyze,
        'rank': cmd_rank,
        'decline': cmd_decline,
        'reschedule': cmd_reschedule,
        'focus': cmd_focus,
        'commute': cmd_commute,
    }
    
    commands[args.command](args)

if __name__ == '__main__':
    main()
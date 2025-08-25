# 📅 Calendar Agent

An intelligent calendar management system that automates schedule optimization, meeting prioritization, and time blocking. Calendar Agent acts as your personal scheduling assistant, analyzing your calendar patterns and helping you reclaim focus time.

<p align="center">
  <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Google%20Calendar-API%20v3-green.svg" alt="Google Calendar API">
  <img src="https://img.shields.io/badge/license-MIT-brightgreen.svg" alt="MIT License">
</p>

## Why Calendar Agent?

Calendar Agent understands that your time is your most valuable resource. It analyzes your meeting patterns, identifies time wasters, and helps you create meaningful focus blocks for deep work.

## ✨ Features

### 🎯 Smart Meeting Management
- **Automatic Priority Ranking** - AI-powered meeting importance classification
- **One-Click Decline** - Decline meetings with automatic notifications
- **Smart Rescheduling** - Reschedule with conflict detection and attendee notifications
- **Batch Operations** - Process multiple meetings at once

### 📊 Schedule Analytics
- **Time Analysis** - Track focus time vs meeting time
- **Free Block Detection** - Automatically find available time slots
- **Back-to-Back Detection** - Identify meeting fatigue patterns
- **Daily/Weekly Insights** - Understand your time allocation

### 🚀 Productivity Features
- **Focus Blocks** - Protected deep work time with automatic color coding
- **Commute Blocks** - Buffer time between meetings
- **Smart Defaults** - IST timezone, sensible reminders, intuitive categorization
- **CLI & API** - Use via command line or integrate programmatically

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Google account with Calendar access
- Google Cloud Project with Calendar API enabled

### Installation

1. **Clone Calendar Agent**
```bash
git clone https://github.com/yourusername/calendar-agent.git
cd calendar-agent
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Google Calendar API**

   a. Go to [Google Cloud Console](https://console.cloud.google.com/)
   
   b. Create a new project or select existing one
   
   c. Enable Google Calendar API:
   ```bash
   # Direct link to enable API
   open https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
   ```
   
   d. Create credentials:
   - Navigate to [Credentials page](https://console.cloud.google.com/apis/credentials)
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the credentials JSON

4. **Configure credentials**
```bash
# Place your credentials file in the project directory
mv ~/Downloads/client_secret_*.json credentials.json

# Run initial authentication
python -c "from calendar_manager import CalendarManager; CalendarManager()"
# This will open a browser for authentication
```

## 📖 Using Calendar Agent

### Command Line Interface

Calendar Agent provides a simple CLI for all operations:

View today's schedule:
```bash
python cal_cli.py today
```

Analyze your schedule:
```bash
python cal_cli.py analyze

# Output:
# 📊 Schedule Analysis
# Total Meetings: 12
# Focus Time: 3.5 hours
# Meeting Time: 7.0 hours
# Back-to-back Meetings: 8
```

Stack rank meetings by importance:
```bash
python cal_cli.py rank

# Output:
# 🔴 Critical - Do Not Cancel
#    • 4:00 PM - Production Deployment
# 🟡 Important - Try to Keep  
#    • 2:00 PM - Team Weekly
# 🟢 Moderate - Can Reschedule
#    • 3:30 PM - 1:1 Sync
# 🔵 Cancel Candidates
#    • 1:15 PM - Optional Standup
```

Decline a meeting:
```bash
python cal_cli.py decline "Optional Standup"
```

Reschedule a meeting:
```bash
python cal_cli.py reschedule "Team Sync" --shift-minutes 30 --message "Running late from previous meeting"
```

Create focus time:
```bash
python cal_cli.py focus "Deep Work" 14:00 17:00 --description "Quarterly planning"
```

Add buffer time:
```bash
python cal_cli.py commute 13:00 13:30 --description "Lunch break"
```

### Programmatic Usage

Calendar Agent can also be used as a Python library:

```python
from calendar_manager import CalendarManager
from datetime import datetime, timedelta

# Initialize Calendar Agent
manager = CalendarManager()

# Get today's events
events = manager.get_today_events()
for event in events:
    print(f"{event.start.strftime('%H:%M')} - {event.title}")

# Smart meeting ranking
rankings = manager.stack_rank_meetings()
cancelable = rankings['cancelable']
print(f"You can free up {sum(e.duration_minutes for e in cancelable)} minutes")

# Find free time blocks
analysis = manager.analyze_schedule()
for start, end in analysis['free_blocks']:
    duration = (end - start).total_seconds() / 60
    if duration >= 60:  # Find 1+ hour blocks
        print(f"Free block: {start.strftime('%H:%M')} - {end.strftime('%H:%M')}")

# Batch decline low-priority meetings
for event in cancelable:
    manager.decline_event(event.id)
    print(f"Declined: {event.title}")

# Create focus blocks in free time
now = datetime.now()
start = now.replace(hour=14, minute=0)
end = now.replace(hour=17, minute=0)
manager.create_focus_block("Strategic Planning", start, end)
```

## 🏗️ Architecture

```
calendar-agent/
├── calendar_manager.py    # Core business logic & API abstraction
├── cal_cli.py             # Command-line interface
├── .claude/
│   ├── CLAUDE.md          # Your personal preferences (git-ignored)
│   └── CLAUDE.md.example  # Template for configuration
├── credentials.json       # Google OAuth credentials (git-ignored)
├── token.pickle          # Cached auth token (git-ignored)
└── requirements.txt      # Python dependencies
```

### Core Components

- **`CalendarManager`** - High-level calendar operations
- **`CalendarEvent`** - Structured event representation  
- **`EventStatus`** - Event response status enum
- **`EventColor`** - Visual categorization system

## 🔧 Configuration

### Personal Preferences File

Create your personal configuration by copying the example:

```bash
mkdir -p .claude
cp .claude/CLAUDE.md.example .claude/CLAUDE.md
```

Edit `.claude/CLAUDE.md` to set:
- Your working hours and timezone
- Meeting preferences and rules
- Company domains (for internal/external classification)
- Custom priority keywords
- Personal calendar rules

This file is gitignored and won't be committed to version control.

### Environment Variables (Optional)

```bash
# Set default timezone (defaults to Asia/Kolkata)
export CAL_TIMEZONE="America/New_York"

# Set working hours for free block detection
export CAL_WORK_START="09:00"
export CAL_WORK_END="18:00"
```

### Customizing Meeting Priority

Edit the ranking logic in `calendar_manager.py`:

```python
# Add your own keywords for critical meetings
CRITICAL_KEYWORDS = ['production', 'deploy', 'customer', 'board']
CANCELABLE_KEYWORDS = ['optional', 'maybe', 'casual']
```

## 🎯 How Calendar Agent Helps

### 1. Daily Schedule Optimization
Start your day by letting Calendar Agent analyze and optimize:
```bash
# Morning routine with Calendar Agent
python cal_cli.py analyze
python cal_cli.py rank
# Calendar Agent identifies low-value meetings
# Create focus blocks for important work
```

### 2. Meeting Preparation
```python
# Find back-to-back meetings and add breaks
manager = CalendarManager()
events = manager.get_today_events()
for i in range(len(events)-1):
    gap = (events[i+1].start - events[i].end).total_seconds() / 60
    if gap < 15:  # Add 15-min break
        manager.create_commute_block(
            events[i].end,
            events[i].end + timedelta(minutes=15),
            "Break"
        )
```

### 3. Weekly Time Audit
```python
# Analyze time allocation over past week
for day in range(7):
    date = datetime.now().date() - timedelta(days=day)
    analysis = manager.analyze_schedule(date)
    print(f"{date}: {analysis['focus_hours']:.1f}h focus, {analysis['meeting_hours']:.1f}h meetings")
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Calendar API team for excellent documentation
- Python community for amazing libraries
- All contributors and users of this project

## 🐛 Troubleshooting

### Common Issues

**Authentication Error**
```bash
# Delete token and re-authenticate
rm token.pickle
python -c "from calendar_manager import CalendarManager; CalendarManager()"
```

**API Quota Exceeded**
- Default quota is 1,000,000 requests/day
- Implement caching for frequently accessed data
- Use batch operations where possible

**Timezone Issues**
```python
# Explicitly set timezone
import pytz
manager = CalendarManager()
manager.IST = pytz.timezone('America/New_York')
```

## 📚 Advanced Examples

### Integration with Slack
```python
# Post daily schedule to Slack
import requests

manager = CalendarManager()
events = manager.get_today_events()
analysis = manager.analyze_schedule()

slack_message = f"Today: {len(events)} events, {analysis['focus_hours']:.1f}h focus time"
requests.post(SLACK_WEBHOOK_URL, json={"text": slack_message})
```

### Auto-declining Recurring Meetings
```python
# Decline all recurring standups on Fridays
for event in manager.get_today_events():
    if "standup" in event.title.lower() and datetime.now().weekday() == 4:
        manager.decline_event(event.id)
```

### Smart Rescheduling
```python
# Find optimal time for postponed meeting
def find_best_slot(manager, duration_minutes=30):
    analysis = manager.analyze_schedule()
    for start, end in analysis['free_blocks']:
        if (end - start).total_seconds() / 60 >= duration_minutes:
            return start
    return None

optimal_time = find_best_slot(manager, 60)
if optimal_time:
    manager.reschedule_event(event.id, optimal_time, optimal_time + timedelta(hours=1))
```

---

<p align="center">
<strong>Calendar Agent</strong> - Your intelligent scheduling assistant<br>
Built with ❤️ for better time management
</p>
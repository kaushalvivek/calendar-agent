# Calendar Management System - Architecture Documentation

## Refactoring Analysis

### Original Scripts Issues
1. **Code Duplication**: Authentication logic repeated in every script
2. **No Abstraction**: Direct API calls scattered throughout
3. **Hard to Maintain**: Changes require updates in multiple places
4. **Limited Reusability**: Each operation was a standalone script
5. **No Error Handling**: Basic exception handling only

### Refactored Architecture

```
┌─────────────────────────────────────┐
│           CLI Interface             │
│          (cal_cli.py)               │
└─────────────┬───────────────────────┘
              │
┌─────────────▼───────────────────────┐
│       Calendar Manager              │
│    (calendar_manager.py)            │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Data Models               │   │
│  │  - CalendarEvent            │   │
│  │  - EventStatus              │   │
│  │  - EventColor               │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Core Operations           │   │
│  │  - Event CRUD               │   │
│  │  - Schedule Analysis        │   │
│  │  - Smart Ranking            │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │   Utilities                 │   │
│  │  - Authentication           │   │
│  │  - Timezone Management      │   │
│  │  - Event Parsing            │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

## Key Improvements

### 1. Single Responsibility Principle
Each component has one clear purpose:
- `CalendarEvent`: Data representation
- `CalendarManager`: Business logic
- `cal_cli.py`: User interface

### 2. Reusable Components

```python
# Before: Repeated in every script
def get_credentials():
    # 20+ lines of auth code
    ...

# After: Single method, used everywhere
manager = CalendarManager()  # Auth handled internally
```

### 3. Type Safety & Structure

```python
# Before: Working with raw dicts
event = {'summary': title, 'start': {...}}

# After: Structured data
event = CalendarEvent(
    title="Meeting",
    start=datetime.now(),
    status=EventStatus.ACCEPTED
)
```

### 4. High-Level Operations

```python
# Before: 50+ lines to create focus block
# After: One line
manager.create_focus_block("Deep Work", start, end)
```

### 5. Smart Analysis

```python
# New capabilities not in original scripts
analysis = manager.analyze_schedule()
rankings = manager.stack_rank_meetings()
free_blocks = manager._find_free_blocks(events)
```

## Usage Patterns

### Pattern 1: Quick CLI Operations
```bash
# Single command for complex operations
python cal_cli.py decline "sync meeting"
python cal_cli.py focus "Project X" 14:00 17:00
```

### Pattern 2: Batch Operations
```python
manager = CalendarManager()
for event in manager.get_today_events():
    if "sync" in event.title.lower():
        manager.decline_event(event.id)
```

### Pattern 3: Schedule Optimization
```python
manager = CalendarManager()
analysis = manager.analyze_schedule()

if analysis['back_to_back_count'] > 5:
    # Find and create buffer blocks
    for start, end in analysis['free_blocks']:
        if (end - start).total_seconds() >= 900:  # 15 min
            manager.create_commute_block(start, end, "Buffer time")
```

## Extension Points

### Adding New Event Types
```python
class CalendarEvent:
    @property
    def is_interview(self) -> bool:
        return "interview" in self.title.lower()
    
    @property
    def priority_score(self) -> int:
        # Custom scoring logic
        ...
```

### Adding New Commands
```python
# In cal_cli.py
def cmd_optimize(args):
    """Auto-optimize schedule"""
    manager = CalendarManager()
    # Implementation
```

### Integration with Other Systems
```python
class EnhancedCalendarManager(CalendarManager):
    def sync_with_jira(self):
        # Sync calendar with project management
        ...
    
    def export_to_timesheet(self):
        # Generate timesheet from calendar
        ...
```

## Performance Optimizations

1. **Caching**: Token cached to disk
2. **Batch Operations**: Single API call for date range
3. **Lazy Loading**: Service initialized only when needed
4. **Efficient Parsing**: Single parse method for all events

## Error Handling Strategy

```python
# Graceful degradation
try:
    manager.decline_event(event_id)
except Exception as e:
    print(f"Error: {e}")
    # Continue with other operations
```

## Future Enhancements

1. **Recurring Events**: Handle series modifications
2. **Conflict Detection**: Warn about double-bookings
3. **AI Integration**: Smart rescheduling suggestions
4. **Multi-Calendar**: Support multiple calendar accounts
5. **Webhooks**: Real-time calendar change notifications
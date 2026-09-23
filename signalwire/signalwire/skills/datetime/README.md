# DateTime Skill

The datetime skill provides current date and time information with timezone support. It allows agents to tell users the current time and date in any timezone around the world.

## Features

The skill covers these capabilities:

- Current time retrieval with timezone support
- Current date retrieval with timezone support
- Automatic timezone conversion using pytz
- Human-readable time and date formatting
- UTC default with custom timezone options

## Requirements

The skill needs one package and no external API:

- **Packages**: `pytz`
- **No external APIs required**

## Parameters

### Optional Parameters

The skill accepts one optional parameter, for SWAIG function configuration:

- `swaig_fields` (dict): Additional SWAIG function configuration
  - `secure` (boolean): Override security settings for the time/date functions
  - `fillers` (dict): Language-specific filler phrases while retrieving time/date
  - Any other SWAIG function parameters

This skill needs no configuration parameters beyond the optional `swaig_fields`, and it works with no setup.

## Tools Created

The skill registers two tools:

- `get_current_time` - Get the current time, optionally in a specific timezone
- `get_current_date` - Get the current date, optionally in a specific timezone

## Usage Examples

### Basic Usage

Add the skill with no parameters, and both tools are available immediately:

```python
# No configuration needed - works immediately
agent.add_skill("datetime")
```

### With Custom Fillers

Add language-specific filler phrases the agent speaks while it looks up the time or date:

```python
agent.add_skill("datetime", {
    "swaig_fields": {
        "fillers": {
            "en-US": [
                "Let me check the time...",
                "Looking up the current date...",
                "Getting the time for you..."
            ],
            "es-ES": [
                "Déjame verificar la hora...",
                "Consultando la fecha actual..."
            ]
        }
    }
})
```

### Disabling Security (if needed)

Set `secure` to `False` to allow the tools to run without authentication:

```python
agent.add_skill("datetime", {
    "swaig_fields": {
        "secure": False  # Allow unauthenticated time/date requests
    }
})
```

## How It Works

### Time Function

`get_current_time` takes one optional argument and returns a formatted string:

- **Input**: Optional timezone parameter (e.g., "America/New_York", "Europe/London")
- **Default**: UTC timezone if no timezone specified
- **Output**: Time in 12-hour format with AM/PM and timezone abbreviation
- **Example**: "The current time is 02:30:45 PM EST"

### Date Function

`get_current_date` follows the same pattern:

- **Input**: Optional timezone parameter for date calculation
- **Default**: UTC timezone if no timezone specified  
- **Output**: Full date in readable format
- **Example**: "Today's date is Friday, December 15, 2023"

### Timezone Support

Both tools share the same timezone handling:

- Uses the `pytz` library for accurate timezone handling
- Supports all standard timezone names (e.g., "America/New_York", "Asia/Tokyo")
- Handles daylight saving time automatically
- Returns an error message for a timezone name `pytz` doesn't recognize

## Function Parameters

Both tools accept the same optional parameter:

- `timezone` (string, optional): Timezone name for the time/date
  - Examples: "America/New_York", "Europe/London", "Asia/Tokyo", "UTC"
  - Default: "UTC" if not specified
  - Invalid timezones will cause an error message to be returned

## Error Handling

Both tools return a message instead of raising an exception:

- **Invalid Timezone**: Returns error message with the invalid timezone name
- **System Issues**: Returns friendly error message for any datetime calculation problems
- **Graceful Fallback**: Continues to work even if timezone data is corrupted

## Common Timezone Examples

`pytz` accepts standard IANA timezone names, including these:

- **US Timezones**: "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"
- **European Timezones**: "Europe/London", "Europe/Paris", "Europe/Berlin", "Europe/Rome"
- **Asian Timezones**: "Asia/Tokyo", "Asia/Shanghai", "Asia/Kolkata", "Asia/Dubai"
- **Other Regions**: "Australia/Sydney", "Africa/Cairo", "America/Sao_Paulo"

## Best Practices

Keep these points in mind when you add this skill to an agent:

1. **Default Behavior**: The skill works immediately without configuration
2. **User Queries**: Handle questions like "What time is it?", "What's today's date?", "What time is it in Tokyo?"
3. **Timezone Validation**: The skill gracefully handles invalid timezone names
4. **Localization**: Use fillers in different languages for multilingual agents
5. **Performance**: No external API calls are required, so responses are immediate

## Agent Integration

When added to an agent, this skill automatically:

- Adds speech recognition hints for time/date related words
- Provides prompt guidance about time/date capabilities
- Enables the agent to respond to time and date questions
- Works with any timezone the user requests

It needs no maintenance once it's added, and it fits customer service agents and general-purpose agents that need to state the time or date.
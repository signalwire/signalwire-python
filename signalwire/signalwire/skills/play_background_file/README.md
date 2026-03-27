# Play Background File Skill

A configurable skill for managing background file playback with custom tool names and multiple file collections. Supports both audio and video files with serverless DataMap execution.

## Features

- **Multiple Instances**: Create different tools with unique names and file sets
- **Dynamic Enum Generation**: Function parameters built from your file configuration
- **Audio & Video Support**: Works with any background file type
- **DataMap Efficiency**: Serverless execution, no agent processing load
- **Post-Processing**: AI speaks first, then executes the action
- **Configurable Wait**: Control attention-getting behavior per file

## Configuration

### Basic Structure

```python
agent.add_skill("play_background_file", {
    "tool_name": "your_custom_tool_name",
    "files": [
        {
            "key": "unique_identifier",
            "description": "Human readable description",
            "url": "https://example.com/file.mp4",
            "wait": True  # Optional, defaults to False
        }
    ]
})
```

### Parameters

- **tool_name** (string): Custom name for the generated SWAIG function (default: "play_background_file")
- **files** (array): List of file objects to manage

### File Object Properties

- **key** (string, required): Unique identifier for the file (alphanumeric, underscores, hyphens only)
- **description** (string, required): Human-readable description used in AI responses
- **url** (string, required): URL to the audio/video file
- **wait** (boolean, optional): Whether to suppress attention-getting behavior during playback (default: false)

## Usage Examples

### Single File Testimonial

```python
agent.add_skill("play_background_file", {
    "tool_name": "play_testimonial",
    "files": [
        {
            "key": "massey_success",
            "description": "Customer success story from Massey Energy",
            "url": "https://tatooine.cantina.cloud/vids/massey.mp4",
            "wait": True
        }
    ]
})
```

**Generated Tool**: `play_testimonial(action)`
**Actions**: `["start_massey_success", "stop"]`

### Multiple Demo Videos

```python
agent.add_skill("play_background_file", {
    "tool_name": "play_demo",
    "files": [
        {
            "key": "product_overview",
            "description": "Product overview demonstration",
            "url": "https://example.com/overview.mp4",
            "wait": False
        },
        {
            "key": "advanced_features",
            "description": "Advanced features walkthrough", 
            "url": "https://example.com/advanced.mp4",
            "wait": True
        }
    ]
})
```

**Generated Tool**: `play_demo(action)`
**Actions**: `["start_product_overview", "start_advanced_features", "stop"]`

### Music Playlist

```python
agent.add_skill("play_background_file", {
    "tool_name": "play_music",
    "files": [
        {
            "key": "jazz",
            "description": "smooth jazz background music",
            "url": "https://example.com/jazz.mp3"
        },
        {
            "key": "classical",
            "description": "classical piano background music",
            "url": "https://example.com/classical.mp3"
        }
    ]
})
```

## Generated SWAIG Function

For the testimonial example above, the skill generates:

```json
{
    "function": "play_testimonial",
    "description": "Control background file playback for play testimonial",
    "parameters": {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "description": "Action to perform. Options: start_massey_success: Customer success story from Massey Energy; stop: Stop any currently playing background file",
                "enum": ["start_massey_success", "stop"]
            }
        },
        "required": ["action"]
    },
    "data_map": {
        "expressions": [
            {
                "string": "${args.action}",
                "pattern": "/start_massey_success/i",
                "output": {
                    "response": "Tell the user you are now going to play Customer success story from Massey Energy for them.",
                    "action": [
                        {
                            "playback_bg": {
                                "file": "https://tatooine.cantina.cloud/vids/massey.mp4",
                                "wait": true
                            }
                        }
                    ],
                    "post_process": true
                }
            },
            {
                "string": "${args.action}",
                "pattern": "/stop/i",
                "output": {
                    "response": "Tell the user you have stopped the background file playback.",
                    "action": [
                        {
                            "stop_playback_bg": true
                        }
                    ],
                    "post_process": true
                }
            }
        ]
    }
}
```

## Execution Flow

1. **AI calls function**: `play_testimonial(action: "start_massey_success")`
2. **DataMap matches pattern**: `/start_massey_success/i`
3. **AI receives instruction**: "Tell the user you are now going to play Customer success story from Massey Energy for them."
4. **AI responds naturally**: The AI interprets this and responds in its own voice
5. **Action executes**: Background video starts playing
6. **User experience**: Natural AI announcement before action

## Multiple Instances

You can add multiple instances of this skill with different tool names:

```python
# Testimonials
agent.add_skill("play_background_file", {
    "tool_name": "play_testimonial",
    "files": [{"key": "massey", "description": "Massey Energy success story", "url": "..."}]
})

# Demos  
agent.add_skill("play_background_file", {
    "tool_name": "play_demo",
    "files": [
        {"key": "overview", "description": "Product overview", "url": "..."},
        {"key": "features", "description": "Advanced features", "url": "..."}
    ]
})

# Music
agent.add_skill("play_background_file", {
    "tool_name": "play_music", 
    "files": [{"key": "jazz", "description": "Jazz music", "url": "..."}]
})
```

This creates three separate tools: `play_testimonial`, `play_demo`, and `play_music`.

## Benefits

- **Reusable**: Same skill manages different file collections
- **Configurable**: Easy to add/remove files without code changes  
- **Efficient**: DataMap serverless execution
- **Type Safe**: Enum parameters prevent invalid file references
- **Natural**: AI speaks before actions with post-processing
- **Maintainable**: Centralized file management logic

## Implementation Notes

- File keys are converted to `start_{key}` enum values
- All tools include a "stop" action to halt playback
- Post-processing is enabled by default for natural conversation flow
- The skill validates all configuration parameters at initialization
- Instance keys combine skill name and tool name for uniqueness 
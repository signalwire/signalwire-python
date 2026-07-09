# Lesson 3: Creating Fred's Basic Structure

Time to bring Fred to life! In this lesson, we'll create Fred's foundation - his personality, voice, and basic configuration.

## Table of Contents

1. [Creating the Agent Class](#creating-the-agent-class)
2. [Defining Fred's Personality](#defining-freds-personality)
3. [Configuring Voice and Language](#configuring-voice-and-language)
4. [Setting Conversation Parameters](#setting-conversation-parameters)
5. [Adding Speech Recognition Hints](#adding-speech-recognition-hints)

---

## Creating the Agent Class

Let's start by creating Fred's basic structure. Create a new file called `fred.py`:

### Step 1: Import and Class Definition

```python
#!/usr/bin/env python3
"""
Fred - The Wikipedia Knowledge Bot

A friendly agent that can search Wikipedia for factual information.
Fred is curious, helpful, and loves sharing knowledge from Wikipedia.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred - Your friendly Wikipedia assistant"""
    
    def __init__(self):
        super().__init__(
            name="Fred",
            route="/fred"
        )
```

**What's happening here:**

- `#!/usr/bin/env python3` - Makes the script executable on Unix systems
- We import `AgentBase` - the foundation class for all agents
- We import `SwaigFunctionResult` - used for returning function results
- `name="Fred"` - The agent's identifier
- `route="/fred"` - The HTTP endpoint (accessible at http://localhost:3000/fred)

## Defining Fred's Personality

Now let's give Fred his friendly personality using the Prompt Object Model (POM):

### Step 2: Add Personality Section

```python
def __init__(self):
    super().__init__(
        name="Fred",
        route="/fred"
    )
    
    # Set up Fred's personality using POM
    self.prompt_add_section(
        "Personality", 
        "You are Fred, a friendly and knowledgeable assistant who loves learning and sharing information from Wikipedia. You're enthusiastic about facts and always eager to help people discover new things."
    )
```

### Step 3: Add Goal and Instructions

```python
    # Define Fred's primary goal
    self.prompt_add_section(
        "Goal",
        "Help users find reliable factual information by searching Wikipedia. Make learning fun and engaging."
    )
    
    # Add specific instructions for Fred's behavior
    self.prompt_add_section(
        "Instructions",
        bullets=[
            "Introduce yourself as Fred when greeting users",
            "Use the search_wiki function whenever users ask about factual topics",
            "Be enthusiastic about sharing knowledge",
            "If Wikipedia doesn't have information, suggest alternative search terms",
            "Make learning conversational and enjoyable",
            "Add interesting context or follow-up questions to engage users"
        ]
    )
```

**POM Sections Explained:**

- **Personality**: Defines Fred's character and tone
- **Goal**: His primary purpose
- **Instructions**: Specific behavioral guidelines (as bullet points)

## Configuring Voice and Language

Let's give Fred a voice! SignalWire supports multiple Text-to-Speech providers:

### Step 4: Add Language Configuration

```python
    # Configure Fred's voice
    self.add_language(
        name="English",
        code="en-US",
        voice="rime.bolt",  # A friendly, energetic voice for Fred
        speech_fillers=[
            "Hmm, let me think...",
            "Oh, that's interesting...",
            "Great question!",
            "Let me see..."
        ]
    )
```

**Voice Configuration:**

- `name`: Display name for the language
- `code`: Language code (en-US for US English)
- `voice`: TTS voice selection
  - Format: `provider.voice_name`
  - Example: `rime.bolt` uses Rime provider with the "bolt" voice
- `speech_fillers`: Phrases used while the AI is "thinking"

### Available Voice Options

```python
# Other voice examples:
# "rime.spore" - Professional, clear
# "rime.marsh" - Deep, authoritative  
# "rime.cove" - Warm, friendly
# "elevenlabs.rachel" - Natural, conversational
```

## Setting Conversation Parameters

Now let's configure how Fred interacts during conversations:

### Step 5: Set AI Parameters

```python
    # Set conversation parameters
    self.set_params({
        "ai_model": "gpt-4.1-nano",       # The AI model to use
        "wait_for_user": True,            # Wait for user to speak first
        "end_of_speech_timeout": 1000,    # Milliseconds of silence before assuming speech ended
        "ai_volume": 7,                   # Voice volume level (1-10)
        "local_tz": "America/New_York"    # Timezone for time-related functions
    })
```

**Parameter Breakdown:**

- `ai_model`: Which OpenAI model to use
  - `gpt-4.1-nano` - Fast, efficient
  - `gpt-4-turbo` - More capable
- `wait_for_user`: Whether to wait for user input or speak first
- `end_of_speech_timeout`: How long to wait during pauses
- `ai_volume`: Speech volume (1=quiet, 10=loud)
- `local_tz`: Default timezone for the agent

### Step 6: Add Global Context

```python
    # Add some context about Fred
    self.set_global_data({
        "assistant_name": "Fred",
        "specialty": "Wikipedia knowledge",
        "personality_traits": ["friendly", "curious", "enthusiastic", "helpful"]
    })
```

This data is available to the AI during conversations, helping maintain consistency.

## Adding Speech Recognition Hints

Help the speech recognition system understand domain-specific terms:

### Step 7: Add Recognition Hints

```python
    # Add hints for better speech recognition
    self.add_hints([
        "Wikipedia",
        "Fred",
        "tell me about",
        "what is",
        "who is",
        "search for",
        "look up"
    ])
```

These hints improve accuracy when users say these phrases.

## Complete Basic Structure

Here's Fred's complete basic structure so far:

```python
#!/usr/bin/env python3
"""
Fred - The Wikipedia Knowledge Bot

A friendly agent that can search Wikipedia for factual information.
Fred is curious, helpful, and loves sharing knowledge from Wikipedia.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred - Your friendly Wikipedia assistant"""
    
    def __init__(self):
        super().__init__(
            name="Fred",
            route="/fred"
        )
        
        # Set up Fred's personality using POM
        self.prompt_add_section(
            "Personality", 
            "You are Fred, a friendly and knowledgeable assistant who loves learning and sharing information from Wikipedia. You're enthusiastic about facts and always eager to help people discover new things."
        )
        
        self.prompt_add_section(
            "Goal",
            "Help users find reliable factual information by searching Wikipedia. Make learning fun and engaging."
        )
        
        self.prompt_add_section(
            "Instructions",
            bullets=[
                "Introduce yourself as Fred when greeting users",
                "Use the search_wiki function whenever users ask about factual topics",
                "Be enthusiastic about sharing knowledge",
                "If Wikipedia doesn't have information, suggest alternative search terms",
                "Make learning conversational and enjoyable",
                "Add interesting context or follow-up questions to engage users"
            ]
        )
        
        # Configure Fred's voice
        self.add_language(
            name="English",
            code="en-US",
            voice="rime.bolt",  # A friendly, energetic voice for Fred
            speech_fillers=[
                "Hmm, let me think...",
                "Oh, that's interesting...",
                "Great question!",
                "Let me see..."
            ]
        )
        
        # Add hints for better speech recognition
        self.add_hints([
            "Wikipedia",
            "Fred",
            "tell me about",
            "what is",
            "who is",
            "search for",
            "look up"
        ])
        
        # Set conversation parameters
        self.set_params({
            "ai_model": "gpt-4.1-nano",
            "wait_for_user": True,
            "end_of_speech_timeout": 1000,
            "ai_volume": 7,
            "local_tz": "America/New_York"
        })
        
        # Add some context about Fred
        self.set_global_data({
            "assistant_name": "Fred",
            "specialty": "Wikipedia knowledge",
            "personality_traits": ["friendly", "curious", "enthusiastic", "helpful"]
        })
```

## Testing the Basic Structure

Add a simple main function to test:

<!-- snippet: no-run illustrative fragment (references `FredTheWikiBot` established in the surrounding prose) -->
```python
def main():
    """Test Fred's basic structure"""
    fred = FredTheWikiBot()
    print(f"✅ Fred created successfully!")
    print(f"   Name: {fred.get_name()}")
    print(f"   Route: /fred")
    print(f"   Ready to add capabilities!")

if __name__ == "__main__":
    main()
```

Run it:
```bash
python fred.py
```

Expected output:
```
✅ Fred created successfully!
   Name: Fred
   Route: /fred
   Ready to add capabilities!
```

## Key Concepts Review

### Prompt Object Model (POM)

POM organizes your agent's instructions into logical sections:
- More maintainable than one long prompt
- Easier to update specific behaviors
- Clear structure for complex agents

### Voice Configuration

- Multiple TTS providers available
- Each voice has different characteristics
- Speech fillers make conversations feel natural

### Global Data

- Provides context throughout the conversation
- Helps maintain consistency
- Can include any JSON-serializable data

## Next Steps

Fred now has personality and voice, but he can't search Wikipedia yet. Let's add that capability!

➡️ Continue to [Lesson 4: Adding the Wikipedia Search Skill](04-wikipedia-skill.md)

---

**Progress Check:**
- [x] Created FredTheWikiBot class
- [x] Defined personality with POM
- [x] Configured voice settings
- [x] Set conversation parameters
- [ ] Add Wikipedia search capability
- [ ] Add custom functions

---

[← Previous: Environment Setup](02-setup.md) | [Back to Overview](README.md) | [Next: Wikipedia Skill →](04-wikipedia-skill.md)

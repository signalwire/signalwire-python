# Lesson 3: Creating Fred's Basic Structure

This lesson builds Fred's foundation: the agent class, the prompt that sets its persona, its voice, and its conversation settings. Fred can't search anything yet. Lesson 4 adds that.

## Table of Contents

1. [Creating the Agent Class](#creating-the-agent-class)
2. [Defining Fred's Personality](#defining-freds-personality)
3. [Configuring Voice and Language](#configuring-voice-and-language)
4. [Setting Conversation Parameters](#setting-conversation-parameters)
5. [Adding Speech Recognition Hints](#adding-speech-recognition-hints)
6. [Testing the Basic Structure](#testing-the-basic-structure)

---

## Creating the Agent Class

Every agent is a class that inherits from `AgentBase`. Create a new file called `fred.py`.

### Step 1: Import and Class Definition

Start with the imports and the class:

```python
#!/usr/bin/env python3
"""
Fred: a Wikipedia knowledge bot

An agent that searches Wikipedia and shares facts about Wikipedia itself,
with a friendly, curious persona.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred, a Wikipedia assistant with a friendly persona"""
    
    def __init__(self):
        super().__init__(
            name="Fred",
            route="/fred"
        )
```

Each line has a job:

- `#!/usr/bin/env python3` lets you run the file directly on Linux and macOS once it's executable
- `AgentBase` is the class every agent inherits from
- `SwaigFunctionResult` is what a function returns to the model (Lesson 5)
- `name="Fred"` is the agent's name
- `route="/fred"` is the agent's HTTP path, so Fred answers at `http://localhost:3000/fred`

## Defining Fred's Personality

The prompt tells the model who Fred is and how to behave. The SDK builds it from named sections, using the Prompt Object Model (POM).

### Step 2: Add Personality Section

The first section sets the persona:

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

Two more sections give Fred a goal and specific instructions:

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

Each section has a purpose:

- **Personality**: Fred's character and tone
- **Goal**: what Fred is for
- **Instructions**: specific behavior, as bullet points

## Configuring Voice and Language

A language entry sets the voice Fred speaks with, and the phrases it can say while it thinks.

### Step 4: Add Language Configuration

Add the language after the prompt sections:

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

The settings work like this:

- `name`: a display name for the language
- `code`: the language code, `en-US` for US English
- `voice`: the text-to-speech voice, written as `provider.voice_name`. `rime.bolt` is the Rime provider's "bolt" voice.
- `speech_fillers`: phrases the platform can say while the model prepares a reply

The agent guide's [list of voice providers](../../../docs/agent_guide.md#voice-providers) shows the voice string format and a sample voice for each provider.

## Setting Conversation Parameters

Parameters control how the conversation runs: which model, who speaks first, and how long a pause ends a turn.

### Step 5: Set AI Parameters

Set the parameters with `set_params`:

```python
    # Set conversation parameters
    self.set_params({
        "ai_model": "gpt-4.1-nano",       # The AI model to use
        "wait_for_user": True,            # Wait for user to speak first
        "end_of_speech_timeout": 1000,    # Milliseconds of silence before assuming speech ended
        "ai_volume": 7,                   # Voice volume adjustment (-50 to 50, default 0)
        "local_tz": "America/New_York"    # Timezone for time-related functions
    })
```

Each parameter has a range the platform accepts:

- `ai_model`: the model that runs the conversation. The SWML schema lists `gpt-4o-mini` (the default), `gpt-4.1-mini` and `gpt-4.1-nano`. Fred uses `gpt-4.1-nano`, the smallest of the three.
- `wait_for_user`: when `True`, the caller speaks first. When `False`, the agent opens the conversation.
- `end_of_speech_timeout`: how many milliseconds of silence end the caller's turn, from 250 to 10,000. The default is 700.
- `ai_volume`: raises or lowers the agent's voice, from -50 to 50. The default is 0.
- `local_tz`: the agent's time zone, as an IANA name

### Step 6: Add Global Data

Global data is session data that travels with the call:

```python
    # Add some context about Fred
    self.set_global_data({
        "assistant_name": "Fred",
        "specialty": "Wikipedia knowledge",
        "personality_traits": ["friendly", "curious", "enthusiastic", "helpful"]
    })
```

The model doesn't see global data unless a prompt refers to a key, such as `${global_data.specialty}`. Functions receive it with every request, so it's a place for facts your code needs during the call.

## Adding Speech Recognition Hints

Hints tell speech recognition which words and phrases to expect.

### Step 7: Add Recognition Hints

Add the words callers are likely to say to Fred:

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

Hints improve recognition accuracy when callers say these words.

## Complete Basic Structure

Here's Fred's structure so far:

```python
#!/usr/bin/env python3
"""
Fred: a Wikipedia knowledge bot

An agent that searches Wikipedia and shares facts about Wikipedia itself,
with a friendly, curious persona.
"""

from signalwire import AgentBase
from signalwire.core.function_result import SwaigFunctionResult

class FredTheWikiBot(AgentBase):
    """Fred, a Wikipedia assistant with a friendly persona"""
    
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

A short `main` function confirms the class builds without starting a server:

<!-- snippet: no-run illustrative fragment (references `FredTheWikiBot` established in the surrounding prose) -->
```python
def main():
    """Test Fred's basic structure"""
    fred = FredTheWikiBot()
    print("Fred created.")
    print(f"   Name: {fred.get_name()}")
    print(f"   Route: /fred")

if __name__ == "__main__":
    main()
```

Run the file to build the agent and print its name:

```bash
python fred.py
```

The output confirms the agent's name and route:

```
Fred created.
   Name: Fred
   Route: /fred
```

## Key Concepts Review

This lesson used three of the SDK's building blocks.

### Prompt Object Model (POM)

POM organizes the prompt into named sections:

- Easier to maintain than one long prompt
- Each behavior can be updated in its own section
- A clear structure as the agent grows

### Voice Configuration

The language entry controls how Fred sounds:

- Several text-to-speech providers are available
- Each voice has its own character
- Speech fillers cover the pause while the model prepares a reply

### Global Data

Global data holds session facts:

- Functions receive it with every request
- The model sees a value only when a prompt refers to it
- It can hold any JSON-serializable data

## Next Steps

Fred has a persona and a voice, but it can't search Wikipedia yet. Continue with [Lesson 4: Adding the Wikipedia Search Skill](04-wikipedia-skill.md).

---

[Previous: Environment Setup](02-setup.md) | [Overview](README.md) | [Next: Wikipedia Skill](04-wikipedia-skill.md)

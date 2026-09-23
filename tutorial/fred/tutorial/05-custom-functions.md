# Lesson 5: Creating Custom Functions

Skills cover common capabilities, and your own functions cover the rest. This lesson writes `share_fun_fact`, a SWAIG function that shares facts about Wikipedia, and explains how the model calls it and what it returns.

## Table of Contents

1. [Understanding SWAIG Functions](#understanding-swaig-functions)
2. [Creating the Fun Fact Function](#creating-the-fun-fact-function)
3. [The @tool Decorator](#the-tool-decorator)
4. [Function Implementation](#function-implementation)
5. [Returning Results](#returning-results)
6. [Testing Custom Functions](#testing-custom-functions)

---

## Understanding SWAIG Functions

SWAIG (SignalWire AI Gateway) functions are tools the model can call during a conversation. They let an agent act, not only talk.

### What Is a SWAIG Function?

A SWAIG function:

- Can be called by the model during a conversation
- Receives arguments the model chooses
- Runs your code, such as an API call or a calculation
- Returns a result the model uses in its reply

### Function Flow

A function call moves through five stages:

```
Caller asks a question → Model calls the function → Your code runs → Result returns to the model → Model answers the caller
```

## Creating the Fun Fact Function

The first version of the function picks a random fact from a list.

### Step 1: Add the Function Decorator

Add this inside Fred's `__init__` method, after the skill configuration:

```python
        # Add a fun fact function
        @self.tool(
            name="share_fun_fact",
            description="Share a fun fact about Wikipedia itself",
            parameters={}
        )
        def share_fun_fact(args, raw_data):
            import random
            facts = [
                "Wikipedia has over 6 million articles in English alone!",
                "Wikipedia is available in more than 300 languages!",
                "Wikipedia was launched on January 15, 2001!",
                "The most edited Wikipedia page is about George W. Bush!",
                "Wikipedia is the 7th most visited website in the world!"
            ]
            fact = random.choice(facts)
            return SwaigFunctionResult(f"Here's a fun Wikipedia fact: {fact}")
```

### Understanding the Code

The function has three parts.

**The decorator** registers the function with the agent:

<!-- snippet: no-compile decorator-fragment (decorator with no function below it) -->
```python
@self.tool(
    name="share_fun_fact",          # Function name the AI will use
    description="Share a fun...",   # Helps AI know when to use it
    parameters={}                   # No parameters needed
)
```

**The signature** receives the model's arguments and the request:

<!-- snippet: no-compile signature-only (function signature with commented-out body) -->
```python
def share_fun_fact(args, raw_data):
    # args: Dictionary of parameters passed by AI
    # raw_data: Full request data (call_id, metadata, etc.)
```

**The body** does the work and returns a result:

<!-- snippet: no-compile method-body-excerpt (statements lifted from inside the function, incl. bare return) -->
```python
import random                       # Import inside function is fine
facts = [...]                       # List of facts
fact = random.choice(facts)         # Pick random fact
return SwaigFunctionResult(f"...")  # Return formatted result
```

## The @tool Decorator

`@self.tool()` registers a function as a SWAIG tool. It takes a name, a description and a parameter schema.

### Decorator Parameters

Each parameter of the decorator has a role:

<!-- snippet: no-compile decorator-fragment (decorator with no function below it) -->
```python
@self.tool(
    name="function_name",           # Required: Unique function identifier
    description="What it does",     # Required: AI uses this to decide when to call
    parameters={                    # Parameter definitions (JSON Schema)
        "param_name": {
            "type": "string",       # JSON Schema type: string, integer, number, boolean
            "description": "...",   # What the parameter is for
            "enum": ["opt1", "opt2"] # Optional: Allowed values
        }
    }
)
```

The description matters more than it looks. The model reads it on every turn to decide when to call the function.

### Example with Parameters

This example function takes two parameters:

```python
@self.tool(
    name="search_by_category",
    description="Search Wikipedia articles in a specific category",
    parameters={
        "category": {
            "type": "string",
            "description": "Category to search in",
            "enum": ["science", "history", "geography", "people"]
        },
        "limit": {
            "type": "number",
            "description": "Maximum results to return",
            "default": 3
        }
    }
)
def search_by_category(args, raw_data):
    category = args.get("category", "general")
    limit = args.get("limit", 3)
    # Implementation here...
    return SwaigFunctionResult(f"Found {limit} articles in {category}")
```

## Function Implementation

The final version groups facts by category, and lets the model ask for one.

### Step 2: Fun Fact Function With Categories

Replace the first version with this one:

```python
        # Enhanced fun fact function with categories
        @self.tool(
            name="share_fun_fact",
            description="Share an interesting fact about Wikipedia itself",
            parameters={
                "category": {
                    "type": "string",
                    "description": "Type of fact to share",
                    "enum": ["statistics", "history", "records", "random"]
                }
            }
        )
        def share_fun_fact(args, raw_data):
            import random
            
            # Get the requested category
            category = args.get("category", "random")
            
            # Define facts by category
            facts = {
                "statistics": [
                    "Wikipedia has over 6 million articles in English alone!",
                    "Wikipedia is available in more than 300 languages!",
                    "Wikipedia receives over 18 billion page views per month!",
                    "There are over 100,000 active Wikipedia contributors!"
                ],
                "history": [
                    "Wikipedia was launched on January 15, 2001!",
                    "The first Wikipedia article was about the letter 'U'!",
                    "Wikipedia's name comes from 'wiki' (Hawaiian for 'quick') and 'encyclopedia'!",
                    "Jimmy Wales and Larry Sanger founded Wikipedia!"
                ],
                "records": [
                    "The most edited Wikipedia page is about George W. Bush!",
                    "The longest Wikipedia article is about California Proposition 8!",
                    "Wikipedia is the 7th most visited website in the world!",
                    "The Wikipedia article on 'List of Pokemon' is one of the most viewed!"
                ],
                "random": []  # Will be filled with all facts
            }
            
            # Combine all facts for random selection
            all_facts = []
            for fact_list in facts.values():
                if fact_list:  # Skip empty random list
                    all_facts.extend(fact_list)
            facts["random"] = all_facts
            
            # Select appropriate fact
            fact_list = facts.get(category, facts["random"])
            if not fact_list:
                return SwaigFunctionResult("I don't have any facts in that category.")
            
            fact = random.choice(fact_list)
            
            # Add category context to response
            if category != "random":
                return SwaigFunctionResult(f"Here's a {category} fact about Wikipedia: {fact}")
            else:
                return SwaigFunctionResult(f"Here's a fun Wikipedia fact: {fact}")
```

### Practices for Function Implementation

Three habits keep functions reliable.

1. **Give every argument a default.** The model may leave an optional argument out.

   <!-- snippet: no-compile method-body-excerpt (indented statement lifted from inside the function) -->
   ```python
   category = args.get("category", "random")  # Always provide defaults
   ```

2. **Handle the empty case.** Return a message the model can pass on, instead of raising an error.

   <!-- snippet: no-compile method-body-excerpt (indented statement lifted from inside the function) -->
   ```python
   if not fact_list:
       return SwaigFunctionResult("I don't have any facts in that category.")
   ```

3. **Say what the result is.** Context in the response helps the model use it.

   ```python
   # Include context in response
   return SwaigFunctionResult(f"Here's a {category} fact: {fact}")
   ```

## Returning Results

A SWAIG function returns a `SwaigFunctionResult`. It carries text for the model, and can also carry actions for the platform to carry out.

### Basic Result

The simplest result is text for the model:

<!-- snippet: no-compile method-body-excerpt (bare return outside a function) -->
```python
return SwaigFunctionResult("Simple text response")
```

### Result with Actions

Helper methods add actions. This one plays an audio file in the background while the conversation continues:

<!-- snippet: no-compile method-body-excerpt (bare return outside a function) -->
```python
result = SwaigFunctionResult("Playing background music")
result.play_background_file("https://example.com/music.mp3")
return result
```

### Multiple Actions

The helpers return the result, so you can chain them. Actions run in order, so here the caller hears the sentence before the transfer starts:

<!-- snippet: no-compile method-body-excerpt (bare return outside a function) -->
```python
return (SwaigFunctionResult("Transferring the caller")
        .say("One moment while I connect you.")
        .connect("+15555550100"))
```

### Common Actions

These helper methods cover the most common actions:

- `say(text)`: speak a fixed sentence
- `connect(destination)`: transfer the call
- `hangup()`: end the call
- `play_background_file(url)`: play audio in the background
- `stop_background_file()`: stop the background audio
- `update_global_data(data)`: change the call's global data
- `send_sms(to_number, from_number, body)`: send a text message

## Testing Custom Functions

The final `main` function starts Fred and lists both capabilities:

```python
def main():
    """Run Fred"""
    print("=" * 60)
    print("Fred: a Wikipedia knowledge bot")
    print("=" * 60)
    print()
    print("Fred searches Wikipedia and shares facts about Wikipedia itself.")
    print()
    print("Questions to try:")
    print("  - Tell me about Albert Einstein")
    print("  - What is quantum physics?")
    print("  - Who was Marie Curie?")
    print("  - Search for information about the solar system")
    print("  - Can you share a fun fact?")
    print()
    
    # Create and run Fred
    fred = FredTheWikiBot()
    
    # Get auth credentials for display
    username, password = fred.get_basic_auth_credentials()
    
    print(f"Fred is available at: http://localhost:{fred.port}/fred")
    print(f"Basic Auth: {username}:{password}")
    print()
    print("Starting Fred. Press Ctrl+C to stop.")
    print("=" * 60)
    
    try:
        fred.run()
    except KeyboardInterrupt:
        print("\nFred stopped.")
```

Lesson 6 runs it.

## Complete Function Reference

Here's the outline of the finished function, with a docstring:

```python
# Inside __init__ method:

# Add a fun fact function
@self.tool(
    name="share_fun_fact",
    description="Share an interesting fact about Wikipedia itself",
    parameters={
        "category": {
            "type": "string",
            "description": "Type of fact to share",
            "enum": ["statistics", "history", "records", "random"]
        }
    }
)
def share_fun_fact(args, raw_data):
    """
    Share interesting facts about Wikipedia
    
    Args:
        args: Dictionary with 'category' parameter
        raw_data: Full request context
        
    Returns:
        SwaigFunctionResult with the fact
    """
    import random
    
    # Implementation as shown in Step 2
```

## Next Steps

Fred can search Wikipedia and share facts about it. Next, run Fred and test both functions. Continue with [Lesson 6: Running and Testing Fred](06-running-testing.md).

---

[Previous: Wikipedia Skill](04-wikipedia-skill.md) | [Overview](README.md) | [Next: Running and Testing](06-running-testing.md)
